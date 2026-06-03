import random
from collections import deque
from typing import Callable, List, Optional, Set, Tuple


class MazeGenerator:
    """Maze generator using recursive backtracker (DFS)."""

    NORTH = 1
    EAST = 2
    SOUTH = 4
    WEST = 8

    DIR_MAP: dict[int, tuple[int, int]] = {
        NORTH: (0, -1),
        SOUTH: (0, 1),
        EAST: (1, 0),
        WEST: (-1, 0),
    }

    OPPOSITE: dict[int, int] = {
        NORTH: SOUTH,
        SOUTH: NORTH,
        EAST: WEST,
        WEST: EAST,
    }

    DIR_STR: dict[int, str] = {
        NORTH: 'N',
        SOUTH: 'S',
        EAST: 'E',
        WEST: 'W',
    }

    PATTERN_42 = [
        "X...XXX",
        "X.....X",
        "XXX.XXX",
        "..X.X..",
        "..X.XXX",
    ]

    def __init__(self, width: int, height: int, seed: int = 0) -> None:
        """Initialize MazeGenerator.

        Args:
            width: Number of columns.
            height: Number of rows.
            seed: Random seed for reproducibility.
        """
        self.width = width
        self.height = height
        self.seed = seed
        if seed != 0:
            random.seed(seed)
        self.grid: List[List[int]] = [
            [15 for _ in range(width)] for _ in range(height)
        ]
        self.reserved: Set[Tuple[int, int]] = set()

    def carve_wall(self, x: int, y: int, direction: int) -> None:
        """Remove wall between cell (x, y) and its neighbor in direction.

        Args:
            x: Column of the cell.
            y: Row of the cell.
            direction: One of NORTH, SOUTH, EAST, WEST.
        """
        self.grid[y][x] &= ~direction
        nx = x + self.DIR_MAP[direction][0]
        ny = y + self.DIR_MAP[direction][1]
        if 0 <= nx < self.width and 0 <= ny < self.height:
            self.grid[ny][nx] &= ~self.OPPOSITE[direction]

    def stamp_42(self) -> bool:
        """Reserve cells forming the '42' pattern in the maze center.

        Returns:
            True if pattern was stamped, False if maze is too small.
        """
        pat_w = len(self.PATTERN_42[0])
        pat_h = len(self.PATTERN_42)

        if self.width < pat_w + 4 or self.height < pat_h + 4:
            print("Warning: Maze too small for '42' pattern.")
            return False

        ox = (self.width - pat_w) // 2
        oy = (self.height - pat_h) // 2

        for r in range(pat_h):
            for c in range(pat_w):
                if self.PATTERN_42[r][c] in ('1', 'X'):
                    self.reserved.add((ox + c, oy + r))
        return True

    def generate(
        self,
        start_pt: Tuple[int, int],
        perfect: bool = True,
        step_callback: Optional[Callable[..., None]] = None,
    ) -> None:
        """Generate maze using recursive backtracker from start_pt.

        Args:
            start_pt: (x, y) starting cell.
            perfect: If True, generates a perfect maze (one path between
                any two cells). If False, adds extra passages.
            step_callback: Optional callback called each generation step.
        """
        visited: Set[Tuple[int, int]] = set(self.reserved)
        stack = [start_pt]
        visited.add(start_pt)

        while stack:
            cx, cy = stack[-1]
            if step_callback:
                step_callback('gen', (cx, cy), None)

            neighbors = []
            for d in [self.NORTH, self.SOUTH, self.EAST, self.WEST]:
                nx = cx + self.DIR_MAP[d][0]
                ny = cy + self.DIR_MAP[d][1]
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if (nx, ny) not in visited:
                        neighbors.append((d, nx, ny))

            if neighbors:
                d, nx, ny = random.choice(neighbors)
                self.carve_wall(cx, cy, d)
                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()

        if not perfect:
            num_extra = (self.width * self.height) // 20
            for _ in range(num_extra):
                x = random.randint(1, self.width - 2)
                y = random.randint(1, self.height - 2)
                if (x, y) not in self.reserved:
                    d = random.choice(
                        [self.NORTH, self.SOUTH, self.EAST, self.WEST]
                    )
                    nx = x + self.DIR_MAP[d][0]
                    ny = y + self.DIR_MAP[d][1]
                    if (
                        0 <= nx < self.width
                        and 0 <= ny < self.height
                        and (nx, ny) not in self.reserved
                    ):
                        self.carve_wall(x, y, d)

        if step_callback:
            step_callback('gen_done', None, None)

    def has_open_area(self) -> bool:
        """Check whether any 3x3 block of cells is fully open.

        Returns:
            True if a 3x3 open area exists, False otherwise.
        """
        for y in range(self.height - 2):
            for x in range(self.width - 2):
                open_area = True
                for dy in range(3):
                    for dx in range(3):
                        cx, cy = x + dx, y + dy
                        cell = self.grid[cy][cx]
                        if dx < 2 and (cell & self.EAST):
                            open_area = False
                            break
                        if dy < 2 and (cell & self.SOUTH):
                            open_area = False
                            break
                    if not open_area:
                        break
                if open_area:
                    return True
        return False

    def solve(
        self,
        start_pt: Tuple[int, int],
        end_pt: Tuple[int, int],
        step_callback: Optional[Callable[..., None]] = None,
    ) -> str:
        """Find shortest path from start_pt to end_pt using BFS.

        Args:
            start_pt: (x, y) entry cell.
            end_pt: (x, y) exit cell.
            step_callback: Optional callback called each solve step.

        Returns:
            String of directions (N/S/E/W) or empty string if unsolvable.
        """
        queue: deque[Tuple[Tuple[int, int], str]] = deque(
            [(start_pt, "")]
        )
        visited: Set[Tuple[int, int]] = {start_pt}

        while queue:
            (cx, cy), path = queue.popleft()

            if step_callback:
                step_callback('solve', (cx, cy), visited)

            if (cx, cy) == end_pt:
                if step_callback:
                    step_callback('solve_done', None, None)
                return path

            cell = self.grid[cy][cx]
            for d in [self.NORTH, self.SOUTH, self.EAST, self.WEST]:
                if (cell & d) == 0:
                    nx = cx + self.DIR_MAP[d][0]
                    ny = cy + self.DIR_MAP[d][1]
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        if (nx, ny) not in visited:
                            visited.add((nx, ny))
                            queue.append(
                                ((nx, ny), path + self.DIR_STR[d])
                            )

        if step_callback:
            step_callback('solve_done', None, None)
        return ""

    def save(
        self,
        filepath: str,
        entry: Tuple[int, int],
        exit_pt: Tuple[int, int],
        path_str: str,
    ) -> None:
        """Write maze to file in hexadecimal format.

        Args:
            filepath: Output file path.
            entry: (x, y) entry coordinates.
            exit_pt: (x, y) exit coordinates.
            path_str: Solution path string (N/S/E/W).
        """
        with open(filepath, 'w') as f:
            for row in self.grid:
                f.write("".join(f"{cell:X}" for cell in row) + "\n")
            f.write("\n")
            f.write(f"{entry[0]},{entry[1]}\n")
            f.write(f"{exit_pt[0]},{exit_pt[1]}\n")
            f.write(f"{path_str}\n")

    def get_grid(self) -> List[List[int]]:
        """Return the raw grid of wall bitmasks.

        Returns:
            2D list of integers where each value encodes cell walls.
        """
        return self.grid
