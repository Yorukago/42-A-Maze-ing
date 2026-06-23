"""
The '42' pattern and its placement maths

Kept in its own module so that both the parser (which must reject entry/exit
cells landing inside the logo) and the generator (which reserves those cells)
can share the same source of truth without importing each other

The pattern is centred in the maze and needs a 2-cell clear border on every
side.  When the maze is too small to fit it, reserved_cells returns an
empty set and no logo is drawn
"""

from typing import List, Set, Tuple

# Rows of the logo.  'X' marks a cell that stays fully walled (part of the
# '42' drawing); '.' marks a normal, carvable cell
PATTERN_1: List[str] = [
    "X...XXX",
    "X.....X",
    "XXX.XXX",
    "..X.X..",
    "..X.XXX"
]

PATTERN_2: List[str] = [
    "..X.XXX",
    ".X....X",
    "XXX.XXX",
    "..X.X..",
    "..X.XXX"
]

PATTERN_3: List[str] = [
    "XX...XX",
    "XX...XX",
    ".......",
    "XX...XX",
    "XX...XX"
]

PATTERN_4: List[str] = [
    "...X...",
    "...X...",
    "XXXXXXX",
    "...X...",
    "...X.."
]

PATTERN_5: List[str] = [
    ".XX..XX.",
    ".XX..XX.",
    "...XX...",
    "..XXXX..",
    "..X..X.."
]


class Pattern():
    pattern: list[str] = []
    pattern_w: int = 0
    pattern_h: int = 0
    border: int = 4

    @classmethod
    def set_pattern(cls, pat: list[str]) -> None:
        cls.pattern = pat
        cls.set_size()

    @classmethod
    def set_size(cls) -> None:
        cls.pattern_w = len(cls.pattern[0])
        cls.pattern_h = len(cls.pattern)

    @classmethod
    def choose_pattern(cls, pattern: int | None) -> None:
        match pattern:
            case 2:
                cls.set_pattern(PATTERN_2)
            case 3:
                cls.set_pattern(PATTERN_3)
            case 4:
                cls.set_pattern(PATTERN_4)
            case 5:
                cls.set_pattern(PATTERN_5)
            case _:
                cls.set_pattern(PATTERN_1)


def _fits(width: int, height: int) -> bool:
    """
    Report whether a width x height maze is large enough for the logo

    Args:
        width:  Maze width in cells
        height: Maze height in cells

    Returns:
        True when the centred logo plus its border fits, else False
    """
    return (width >= Pattern.pattern_w + Pattern.border
            and height >= Pattern.pattern_h + Pattern.border)


def origin(width: int, height: int) -> Tuple[int, int]:
    """
    Return the top-left (x, y) at which the centred logo begins

    Args:
        width:  Maze width in cells
        height: Maze height in cells

    Returns:
        (ox, oy) offset of the logo's top-left corner
    """
    return ((width - Pattern.pattern_w) // 2,
            (height - Pattern.pattern_h) // 2)


def reserved_cells(width: int, height: int) -> Set[Tuple[int, int]]:
    """
    Return every (x, y) cell occupied by the centred '42' logo

    Args:
        width:  Maze width in cells
        height: Maze height in cells

    Returns:
        Set of reserved cell coordinates, or an empty set when the maze is
        too small for the logo
    """
    if not _fits(width, height):
        return set()

    ox, oy = origin(width, height)
    cells: Set[Tuple[int, int]] = set()
    for row in range(Pattern.pattern_h):
        for col in range(Pattern.pattern_w):
            if Pattern.pattern[row][col] == "X":
                cells.add((ox + col, oy + row))
    return cells
