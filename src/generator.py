import random


class MazeGenerator:
    NORTH = 1
    EAST = 2
    SOUTH = 4
    WEST = 8

    # PATTERN_42 = [
    # "1010111",
    # "1010101",
    # "1110101",
    # "0010111",
    # "0010100",
    # "0010100",
    # "0010111"
    # ]

    def __init__(self, width: int, height: int, seed: int = 0):
        self.width = width
        self.height = height
        self.seed = seed
        random.seed(seed)

        self.grid = [[15 for _ in range(width)] for _ in range(height)]

    def carve_wall(self, x: int, y: int, direction: int):
        self.grid[y][x] &= ~direction

    def display_debug(self):
        for row in self.grid:
            print(" ".join(f"{cell:X}" for cell in row))
