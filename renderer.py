"""
Interactive ASCII terminal renderer

The renderer is display-only: it takes a mazegen.MazeResult and draws
it. Animation is a replay of the steps recorded during generation/solving,
the maze is never rebuilt here.  When the user asks for a fresh maze the
renderer rolls a new seed and calls :func:mazegen.generator again, then
replays the new result

The box-drawing output (walls, '42' logo, entry/exit, solution path) is
unchanged from the original project
"""

import os
import sys
import time
from typing import List, Optional, Set, Tuple

from mazegen import Config, generator, MazeResult, Step, \
    NORTH, EAST, SOUTH, WEST, pattern, nearest_free

Cell = Tuple[int, int]

COLORS = {
    "1": ("Pink", "\033[38;5;213m", "\033[38;5;118m"),
    "2": ("Gray", "\033[38;5;250m", "\033[38;5;208m"),
    "3": ("Red", "\033[38;5;196m", "\033[38;5;51m"),
    "4": ("Green", "\033[38;5;46m", "\033[38;5;201m"),
    "5": ("Blue", "\033[38;5;27m", "\033[38;5;226m"),
    "6": ("Cyan", "\033[38;5;51m", "\033[38;5;196m"),
    "7": ("Magenta", "\033[38;5;201m", "\033[38;5;46m"),
    "8": ("Yellow", "\033[38;5;226m", "\033[38;5;27m"),
    "9": ("White", "\033[38;5;231m", "\033[38;5;201m"),
}

RESET = "\033[0m"
EXIT_COLOUR = "\033[38;5;204m"
ENTRY_COLOUR = "\033[38;2;191;0;255m"

BOX_CHARS = {
    0: " ", 1: "╵", 2: "╶", 3: "└",
    4: "╷", 5: "│", 6: "┌", 7: "├",
    8: "╴", 9: "┘", 10: "─", 11: "┴",
    12: "┐", 13: "┤", 14: "┬", 15: "┼",
}


def path_coords(start: Cell, solution: str) -> List[Cell]:
    """
    Turn a direction string into the list of cells it visits

    Args:
        start:    Starting (x, y) cell
        solution: Direction letters — N, S, E, W

    Returns:
        Cells stepped through, in order
    """
    coords: List[Cell] = []
    x, y = start
    for letter in solution:
        if letter == "N":
            y -= 1
        elif letter == "S":
            y += 1
        elif letter == "E":
            x += 1
        elif letter == "W":
            x -= 1
        coords.append((x, y))
    return coords


class MazeRenderer:
    """
    Draw a maze and let the user regenerate, toggle the path, resize, recolour

    Construct it with the first MazeResult; run then loops on the
    interactive menu
    """

    def __init__(self, result: MazeResult) -> None:
        """
        Store the first maze and prime display state

        Args:
            result: The maze to display first
        """
        self.show_path: bool = False  # solution path currently shown?
        self.wall_col: str = COLORS["2"][1]  # wall color
        self.path_col: str = COLORS["1"][1]  # path color
        self.pattern_col: str = COLORS["2"][2]  # 42 logo color

        # are we mid-"gen" or "solve" animation? None = not animating
        self.anim_phase: Optional[str] = None
        # which cell is the animation cursor on right now?
        self.anim_cell: Optional[Cell] = None
        # which cells has the solver explored so far?
        self.anim_seen: Optional[Set[Cell]] = None
        # the wall data we're drawing (returned grid)
        self.grid: List[List[int]] = result.grid

        self._load(result, Config.animate)

    def _load(self, result: MazeResult, animate: bool) -> None:
        """
        Adopt *result* as the current maze and optionally replay its steps

        Args:
            result:  Maze to display
            animate: Replay the recorded build/solve animation when True
        """
        self.result = result
        self.entry = result.entry
        self.exit_pt = result.exit
        self.solution = result.solution
        self.path_cells = path_coords(result.entry, result.solution)
        self.grid = result.grid

        os.system("clear")
        if animate:
            self._replay(result.steps)
        else:
            self.render()

    def _regenerate(
        self,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> None:
        """
        Build a fresh maze with a new seed and display it

        Args:
            width:  Optional new width
            height: Optional new height
        """
        if width is not None:
            Config.width = width
        if height is not None:
            Config.height = height
        Config.new_seed()
        self._load(generator(), Config.animate)

    def _replay(self, steps: List[Step]) -> None:
        """
        Play back recorded steps, carving the maze open as it goes

        Drawing starts from a fully-closed grid (every cell walled, the '42'
        logo already in place) and opens one wall per generation frame, so the
        viewer watches the corridors being carved.  Once generation ends the
        grid matches the finished maze and the solve frames play over it

        Generation frames advance quickly; solving frames a touch slower

        Args:
            steps: The recorded Step list from a MazeResult
        """
        # All-closed grid; the '42' cells simply stay closed throughout
        self.grid = [[15] * Config.width for _ in range(Config.height)]

        for step in steps:
            self.anim_phase = step.phase
            self.anim_cell = step.cell
            self.anim_seen = step.seen
            if step.carve is not None:
                self._apply_carve(step.carve)
            self.render()
            time.sleep(0.01 if step.phase == "gen" else 0.005)

        # Finished: show the real grid (includes braid loops not in the
        # gen steps) and clear animation markers
        self.grid = self.result.grid
        self.anim_phase = None
        self.anim_cell = None
        self.anim_seen = None
        self.render()

    def _apply_carve(self, carve: Tuple[int, int, int]) -> None:
        """Open a wall in the replay grid on both adjoining cells"""
        x, y, direction = carve
        opposite = {NORTH: SOUTH, SOUTH: NORTH, EAST: WEST, WEST: EAST}
        self.grid[y][x] &= ~direction
        offset = {NORTH: (0, -1), SOUTH: (0, 1), EAST: (1, 0), WEST: (-1, 0)}
        dx, dy = offset[direction]
        nx, ny = x + dx, y + dy
        if 0 <= nx < Config.width and 0 <= ny < Config.height:
            self.grid[ny][nx] &= ~opposite[direction]

    def _v_wall(self, vx: int, y: int) -> bool:
        """Return True if a vertical wall sits at edge vx on row y"""
        grid = self.grid
        if y < 0 or y >= Config.height:
            return False
        if vx == 0:
            return bool(grid[y][0] & WEST)
        if vx == Config.width:
            return bool(grid[y][vx - 1] & EAST)
        return bool(grid[y][vx] & WEST)

    def _h_wall(self, x: int, vy: int) -> bool:
        """Return True if a horizontal wall sits at edge vy on column x"""
        grid = self.grid
        if x < 0 or x >= Config.width:
            return False
        if vy == 0:
            return bool(grid[0][x] & NORTH)
        if vy == Config.height:
            return bool(grid[vy - 1][x] & SOUTH)
        return bool(grid[vy][x] & NORTH)

    def _is_pattern(self, x: int, y: int) -> bool:
        """Return True if (x, y) is a reserved '42' logo cell"""
        if x < 0 or x >= Config.width or y < 0 or y >= Config.height:
            return False
        return (x, y) in self.result.reserved

    def _vertex_col(self, vx: int, vy: int) -> str:
        """Pick the colour for the junction at (vx, vy)"""
        if (
            self._is_pattern(vx - 1, vy - 1)
            or self._is_pattern(vx, vy - 1)
            or self._is_pattern(vx - 1, vy)
            or self._is_pattern(vx, vy)
        ):
            return self.pattern_col
        return self.wall_col

    def render(self) -> None:
        """
        Draw the current maze to the terminal with box-drawing characters

        Vertex rows draw wall junctions; cell rows draw passages plus entry,
        exit, solution, and live animation markers. Identical in look to the
        original renderer
        """
        sys.stdout.write("\033[H")
        width, height = Config.width, Config.height
        lines: List[str] = []

        for vy in range(height + 1):
            row = ""
            for vx in range(width + 1):
                n = self._v_wall(vx, vy - 1)
                s = self._v_wall(vx, vy)
                e = self._h_wall(vx, vy)
                w = self._h_wall(vx - 1, vy)
                mask = (1 if n else 0) | (2 if e else 0) \
                    | (4 if s else 0) | (8 if w else 0)
                row += self._vertex_col(vx, vy) + BOX_CHARS[mask] + RESET
                if vx < width:
                    is_pat = (
                        self._is_pattern(vx, vy - 1)
                        or self._is_pattern(vx, vy)
                    )
                    edge = self.pattern_col if is_pat else self.wall_col
                    row += (edge + "───" + RESET) if self._h_wall(vx, vy) \
                        else "   "
            lines.append(row)

            if vy < height:
                lines.append(self._cell_row(vy))

        for line in lines:
            sys.stdout.write(line + "\033[K\n")

    def _in_bounds(self, width: int, height: int) -> bool:
        """Return True when entry and exit both lie inside a widthxheight grid
        and neither sits on the '42' logo."""
        entry, exit_pt = Config.entry, Config.exit
        inside = (
            0 <= entry[0] < width and 0 <= entry[1] < height
            and 0 <= exit_pt[0] < width and 0 <= exit_pt[1] < height
        )
        if not inside:
            return False
        reserved = pattern.reserved_cells(width, height)
        return entry not in reserved and exit_pt not in reserved

    def _cell_row(self, vy: int) -> str:
        """Build one passage row (cells and their left walls) for row vy"""
        width = Config.width
        row = ""
        for vx in range(width + 1):
            is_pat = self._is_pattern(vx - 1, vy) or self._is_pattern(vx, vy)
            edge = self.pattern_col if is_pat else self.wall_col
            row += (edge + "│" + RESET) if self._v_wall(vx, vy) else " "
            if vx < width:
                row += self._cell_centre(vx, vy)
        return row

    def _cell_centre(self, vx: int, vy: int) -> str:
        """Return the 3-char centre marker for cell (vx, vy)"""
        if (vx, vy) == self.entry:
            return f" {ENTRY_COLOUR}█{RESET} "
        if (vx, vy) == self.exit_pt:
            return f" {EXIT_COLOUR}█{RESET} "
        if self.anim_cell == (vx, vy) and self.anim_phase == "gen":
            return f" {self.path_col}G{RESET} "
        if self.anim_cell == (vx, vy) and self.anim_phase == "solve":
            return f" {self.path_col}S{RESET} "
        if (
            self.show_path
            and self.anim_phase is None
            and (vx, vy) in self.path_cells
        ):
            return f" {self.path_col}•{RESET} "
        if (
            self.anim_phase == "solve"
            and self.anim_seen
            and (vx, vy) in self.anim_seen
        ):
            return f" {self.path_col}░{RESET} "
        return "   "

    def run(self) -> None:
        """Loop on the interactive menu until the user quits"""
        while True:
            os.system("clear")
            self.render()
            print()
            print("=== A-Maze-Ing Controls ===")
            print("1. Re-generate a new maze")
            print("2. Show/Hide path")
            print("3. Change maze size")
            print("4. Change colors")
            print(f"5. Change pattern ({Config.pat}, min size: "
                  f"{pattern.Pattern.pattern_w + 4}x"
                  f"{pattern.Pattern.pattern_h + 4})")
            print(f"6. Animation: {'ON' if Config.animate else 'OFF'}")
            print(f"7. Perfect maze: {'True' if Config.perfect else 'False'}")
            print("8. Quit\n")
            try:
                choice = input("Choice? (1-7): ").strip()
            except (KeyboardInterrupt, EOFError):
                break

            if choice in ("8", "q", "Q"):
                break
            elif choice == "1":
                self._regenerate()
            elif choice == "2":
                self.show_path = not self.show_path
            elif choice == "3":
                self._resize()
            elif choice == "4":
                self._recolour()
            elif choice == "5":
                self._choose_pattern()
            elif choice == "6":
                Config.animate = not Config.animate
            elif choice == "7":
                Config.perfect = not Config.perfect

        os.system("clear")

    def _choose_pattern(self) -> None:
        """Change pattern in config"""
        if Config.pat == 5:
            Config.pat = 1
        else:
            Config.pat += 1
        pattern.Pattern.choose_pattern(Config.pat)

    def _resize(self) -> None:
        """Prompt for new dimensions and regenerate if valid."""
        try:
            width = int(input("New width (min 2): "))
            height = int(input("New height (min 2): "))
        except ValueError:
            print("Invalid number!")
            time.sleep(2)
            return

        if width <= 1 or height <= 1:
            print("Maze too small, minimum size is 2x2!")
            time.sleep(2)
            return

        if not self._in_bounds(width, height):
            nearest_free(Config.entry,
                         pattern.reserved_cells(Config.width, Config.height))
            nearest_free(Config.exit,
                         pattern.reserved_cells(Config.width, Config.height))

        self._regenerate(width=width, height=height)

    def _recolour(self) -> None:
        """Prompt for wall and path colours and apply them."""
        print("\n--- Available Colors ---")
        for key, value in COLORS.items():
            print(f"{key}. {value[0]}")
        try:
            primary = input("Wall color (1-9): ").strip()
            secondary = input("Path color (1-9): ").strip()
        except (KeyboardInterrupt, EOFError):
            return
        if primary in COLORS and secondary in COLORS:
            self.wall_col = COLORS[primary][1]
            self.path_col = COLORS[secondary][1]
            self.pattern_col = COLORS[primary][2]
        else:
            print("Invalid selection!")
            time.sleep(1)
