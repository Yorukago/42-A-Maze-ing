"""
Maze generation, solving, and serialisation

The :class:MazeGenerator builds a maze with the recursive backtracker (DFS)
and solves it with breadth-first search (BFS).  Generation and solving both
*record every step into a list* rather than driving a live callback: the
renderer later replays that list to animate, so the maze is built exactly
once

Wall encoding — each cell is a 4-bit mask, a set bit meaning a wall is
present: NORTH=1, EAST=2, SOUTH=4, WEST=8.  The grid is row-major:
grid[y][x]

The public entry point is generator(), which runs the whole process
against Config and returns a MazeResult
"""

import random
from collections import deque
from typing import Dict, List, Optional, Set, Tuple
from .config import Config
from . import pattern

Cell = Tuple[int, int]

# Wall bit flags.
NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8

# Direction flag -> (dx, dy) movement
DELTA: Dict[int, Cell] = {NORTH: (0, -1), SOUTH: (0, 1), EAST: (1, 0),
                          WEST: (-1, 0)}
# Direction flag -> the wall on the far side of the shared edge
OPPOSITE: Dict[int, int] = {NORTH: SOUTH, SOUTH: NORTH, EAST: WEST, WEST: EAST}
# Direction flag -> path letter
LETTER: Dict[int, str] = {NORTH: "N", SOUTH: "S", EAST: "E", WEST: "W"}
# Letter -> (dx, dy), the inverse of LETTER/DELTA for path walking
STEP: Dict[str, Cell] = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}

_ORDER = (NORTH, SOUTH, EAST, WEST)


class Step:
    """
    A single recorded animation frame

    Attributes:
        phase: 'gen' while carving, 'solve' while exploring
        cell:  The cell active on this frame
        carve: The wall opened on this frame as (x, y, direction), or None
               for the start cell, backtrack frames, and solve frames
        seen:  Cells visited so far during solving (None during generation)
    """

    def __init__(
        self,
        phase: str,
        cell: Cell,
        carve: Optional[Tuple[int, int, int]] = None,
        seen: Optional[Set[Cell]] = None,
    ) -> None:
        self.phase = phase
        self.cell = cell
        self.carve = carve
        self.seen = seen


class MazeResult:
    """
    Everything the renderer and the output file need from one maze

    Attributes:
        grid:     2D row-major grid of 4-bit wall masks
        entry:    Resolved (x, y) entry cell
        exit:     Resolved (x, y) exit cell
        solution: Shortest path as N/E/S/W letters (empty if unsolvable)
        steps:    Ordered build-then-solve frames for animation
        reserved: Cells occupied by the '42' logo
    """

    def __init__(
        self,
        grid: List[List[int]],
        entry: Cell,
        exit: Cell,
        solution: str,
        steps: Optional[List[Step]] = None,
        reserved: Optional[Set[Cell]] = None,
    ) -> None:
        self.grid = grid
        self.entry = entry
        self.exit = exit
        self.solution = solution
        # Default to a fresh empty list/set per instance
        self.steps = steps if steps is not None else []
        self.reserved = reserved if reserved is not None else set()


class MazeGenerator:
    """
    Build and solve a single maze, recording animation steps as it goes
    """

    def __init__(self, width: int, height: int, seed: int) -> None:
        """
        Create a fully-walled grid and seed the RNG

        Args:
            width:  Maze width in cells
            height: Maze height in cells
            seed:   Seed for reproducible generation
        """
        self.width = width
        self.height = height
        # minecraft seed type of gen!!
        self.rng = random.Random(seed)
        # 15 == 0b1111 == all four walls present
        self.grid: List[List[int]] = [
            [15] * width for _ in range(height)
        ]
        self.reserved: Set[Cell] = pattern.reserved_cells(width, height)
        self.steps: List[Step] = []

    def _in_bounds(self, x: int, y: int) -> bool:
        """Return True when (x, y) lies inside the grid"""
        return 0 <= x < self.width and 0 <= y < self.height

    def _carve(self, x: int, y: int, direction: int) -> None:
        """
        Open the wall between (x, y) and its neighbour in *direction*

        Clears the bit on both cells so neighbouring data stays coherent
        """
        self.grid[y][x] &= ~direction
        dx, dy = DELTA[direction]
        nx, ny = x + dx, y + dy
        if self._in_bounds(nx, ny):
            self.grid[ny][nx] &= ~OPPOSITE[direction]

    def generate(self, start: Cell) -> None:
        """
        Carve a perfect maze from *start* with the recursive backtracker

        Reserved '42' cells are pre-marked as visited so they are never
        carved.  Each visited cell is recorded as a 'gen' step

        Args:
            start: (x, y) cell to begin carving from
        """
        visited: Set[Cell] = set(self.reserved)
        visited.add(start)
        stack: List[Cell] = [start]
        # First frame: the start cell, nothing carved yet
        self.steps.append(Step("gen", start))

        while stack:
            cx, cy = stack[-1]

            options = []
            for direction in _ORDER:
                dx, dy = DELTA[direction]
                nx, ny = cx + dx, cy + dy
                if self._in_bounds(nx, ny) and (nx, ny) not in visited:
                    options.append((direction, nx, ny))

            if options:
                direction, nx, ny = self.rng.choice(options)
                self._carve(cx, cy, direction)
                visited.add((nx, ny))
                stack.append((nx, ny))
                # Frame: moved into (nx, ny) by opening this wall
                self.steps.append(
                    Step("gen", (nx, ny), carve=(cx, cy, direction))
                )
            else:
                stack.pop()
                if stack:
                    # Frame: backtracked to the cell now on top
                    self.steps.append(Step("gen", stack[-1]))

    def braid(self, solution: str, start: Cell, minimum: int = 2) -> None:
        """
        Open extra walls so at least *minimum* routes reach the exit

        First it guarantees a second route by opening a wall between two
        non-adjacent cells of the current solution (such a wall is closed by
        definition, else BFS would already have used it)  It then opens a
        few more random interior walls for variety, never touching reserved
        cells and never creating a 3x3 fully-open area

        Args:
            solution: Current shortest path (N/E/S/W letters)
            start:    (x, y) entry cell, where *solution* begins
            minimum:  Lowest number of distinct exit routes to guarantee
        """
        routes = 1
        if minimum >= 2 and self._open_shortcut(solution, start):
            routes = 2

        extra = max(1, (self.width * self.height) // 20)
        attempts = 0
        opened = 0
        while opened < extra and attempts < extra * 20:
            attempts += 1
            x = self.rng.randrange(self.width)
            y = self.rng.randrange(self.height)
            if (x, y) in self.reserved:
                continue
            direction = self.rng.choice(_ORDER)
            if not (self.grid[y][x] & direction):
                continue  # already open
            dx, dy = DELTA[direction]
            nx, ny = x + dx, y + dy
            if not self._in_bounds(nx, ny) or (nx, ny) in self.reserved:
                continue
            self.grid[y][x] &= ~direction
            self.grid[ny][nx] &= ~OPPOSITE[direction]
            if self.has_open_area():
                # Undo: re-close the wall, it made too large an opening
                self.grid[y][x] |= direction
                self.grid[ny][nx] |= OPPOSITE[direction]
                continue
            opened += 1
            routes += 1

    def _open_shortcut(self, solution: str, start: Cell) -> bool:
        """
        Open one wall joining two non-adjacent solution cells

        Such a wall is guaranteed closed (otherwise BFS would have taken the
        shortcut), so opening it adds a genuinely distinct second route while
        the original path still works

        Returns:
            True if a shortcut was opened, False when none exists
        """
        coords: List[Cell] = [start]
        x, y = start
        for letter in solution:
            dx, dy = STEP[letter]
            x, y = x + dx, y + dy
            coords.append((x, y))

        position = {cell: i for i, cell in enumerate(coords)}
        candidates: List[Tuple[int, int, int]] = []
        for i, (cx, cy) in enumerate(coords):
            for direction in _ORDER:
                dx, dy = DELTA[direction]
                neighbour = (cx + dx, cy + dy)
                j = position.get(neighbour)
                if j is not None and abs(j - i) >= 2:
                    candidates.append((cx, cy, direction))

        if not candidates:
            return False
        cx, cy, direction = self.rng.choice(candidates)
        self._carve(cx, cy, direction)
        return True

    def has_open_area(self) -> bool:
        """
        Report whether any 3x3 block of cells is completely wall-free

        Used as a guard while braiding so the subject's "no 3x3 open area"
        rule is never broken

        Returns:
            True if a fully-open 3x3 area exists, else False
        """
        for y in range(self.height - 2):
            for x in range(self.width - 2):
                if self._block_is_open(x, y):
                    return True
        return False

    def _block_is_open(self, x: int, y: int) -> bool:
        """Return True if the 3x3 block with top-left (x, y) has no walls"""
        for dy in range(3):
            for dx in range(3):
                cell = self.grid[y + dy][x + dx]
                if dx < 2 and (cell & EAST):
                    return False
                if dy < 2 and (cell & SOUTH):
                    return False
        return True

    def solve(self, start: Cell, goal: Cell) -> str:
        """
        Find the shortest start-to-goal path with BFS, recording steps

        Args:
            start: (x, y) entry cell
            goal:  (x, y) exit cell

        Returns:
            Shortest path as N/E/S/W letters, or "" if the goal is unreachable
        """
        queue: deque[Tuple[Cell, str]] = deque([(start, "")])
        visited: Set[Cell] = {start}

        while queue:
            (cx, cy), path = queue.popleft()
            self.steps.append(Step("solve", (cx, cy), seen=set(visited)))

            if (cx, cy) == goal:
                return path

            cell = self.grid[cy][cx]
            for direction in _ORDER:
                if cell & direction:
                    continue  # wall present, cannot pass
                dx, dy = DELTA[direction]
                nx, ny = cx + dx, cy + dy
                if self._in_bounds(nx, ny) and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + LETTER[direction]))
        return ""

    def save(self, path: str, entry: Cell, exit_pt: Cell,
             solution: str) -> None:
        """
        Write the maze to *path* in the subject's hex format

        Layout: HEIGHT rows of WIDTH hex digits, a blank line, the entry and
        exit coordinates, then the solution path.  Every line ends in \\n

        Args:
            path:     Output file path
            entry:    (x, y) entry cell
            exit_pt:  (x, y) exit cell
            solution: Solution path letters
        """
        with open(path, "w") as handle:
            for row in self.grid:
                handle.write("".join(f"{cell:X}" for cell in row) + "\n")
            handle.write("\n")
            handle.write(f"{entry[0]},{entry[1]}\n")
            handle.write(f"{exit_pt[0]},{exit_pt[1]}\n")
            handle.write(f"{solution}\n")


def nearest_free(start: Cell, reserved: Set[Cell],
                 avoid: Optional[Set[Cell]] = None) -> Cell:
    """
    Find the cell nearest *start* that is neither reserved nor avoided

    A breadth-first ring search guarantees the closest valid cell.  Used to
    nudge an entry or exit out of the '42' logo if it would land there

    Args:
        start:    Preferred (x, y) cell (already in bounds)
        reserved: Cells occupied by the logo
        avoid:    Extra cells to skip (e.g. the chosen entry when placing
                  the exit)

    Returns:
        Nearest valid (x, y) cell

    Raises:
        ValueError: If no valid cell exists at all
    """

    avoid = avoid or set()
    width, height = Config.width, Config.height
    queue: deque[Cell] = deque([start])
    seen: Set[Cell] = {start}

    while queue:
        x, y = queue.popleft()
        if (x, y) not in reserved and (x, y) not in avoid:
            return (x, y)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in seen:
                seen.add((nx, ny))
                queue.append((nx, ny))
    raise ValueError("No free cell available for entry/exit.")


def generator() -> MazeResult:
    """
    Runs the entire process with Config and return a MazeResult

    Steps: resolve entry/exit around the '42' logo, build the maze (DFS),
    solve it (BFS), braid in extra routes when Config.perfect is False
    (guaranteeing at least two ways to the exit), write the hex output file,
    and return everything

    parser() must have populated Config first

    Returns:
        MazeResult with grid, entry, exit, solution, and the
        recorded animation steps
    """

    # get reserved cells for 42 pattern
    reserved = pattern.reserved_cells(Config.width, Config.height)

    # get nearest free cell that is neither reserved nor avoid
    entry = nearest_free(Config.entry, reserved)
    exit_pt = nearest_free(Config.exit, reserved, avoid={entry})  # to remove

    # update entry and exit in config
    Config.entry, Config.exit = entry, exit_pt

    # create an instance of maze generator class
    maze = MazeGenerator(Config.width, Config.height, Config.seed)

    # generate maze
    maze.generate(entry)

    # solve the maze
    solution = maze.solve(entry, exit_pt)

    # make maze imperfect
    if not Config.perfect:
        maze.braid(solution, entry, minimum=2)
        solution = maze.solve(entry, exit_pt)

    # create output file
    maze.save(Config.output, entry, exit_pt, solution)

    return MazeResult(
        grid=maze.grid,
        entry=entry,
        exit=exit_pt,
        solution=solution,
        steps=maze.steps,
        reserved=maze.reserved
    )
