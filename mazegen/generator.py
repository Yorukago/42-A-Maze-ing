import random
from collections import deque
from typing import List, Tuple, Set

class MazeGenerator:
    NORTH = 1
    EAST = 2
    SOUTH = 4
    WEST = 8

    DIR_MAP = {
        NORTH: (0, -1),
        SOUTH: (0, 1),
        EAST: (1, 0),
        WEST: (-1, 0)
    }

    OPPOSITE = {
        NORTH: SOUTH,
        SOUTH: NORTH,
        EAST: WEST,
        WEST: EAST
    }

    DIR_STR = {
        NORTH: 'N',
        SOUTH: 'S',
        EAST: 'E',
        WEST: 'W'
    }

    PATTERN_42 = [
        "X...XXX",
        "X.....X",
        "XXX.XXX",
        "..X.X..",
        "..X.XXX",
    ]

    def __init__(self, width: int, height: int, seed: int = 0):
        self.width = width
        self.height = height
        self.seed = seed
        if seed != 0:
            random.seed(seed)

        self.grid = [[15 for _ in range(width)] for _ in range(height)]
        self.reserved: Set[Tuple[int, int]] = set()

    def carve_wall(self, x: int, y: int, direction: int):
        self.grid[y][x] &= ~direction
        nx, ny = x + self.DIR_MAP[direction][0], y + self.DIR_MAP[direction][1]
        if 0 <= nx < self.width and 0 <= ny < self.height:
            self.grid[ny][nx] &= ~self.OPPOSITE[direction]

    def stamp_42(self) -> bool:
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

    def generate(self, start_pt: Tuple[int, int], perfect: bool = True, step_callback=None):
        visited = set(self.reserved)
        stack = [start_pt]
        visited.add(start_pt)

        while stack:
            cx, cy = stack[-1]
            if step_callback:
                step_callback('gen', (cx, cy), None)

            neighbors = []
            for d in [self.NORTH, self.SOUTH, self.EAST, self.WEST]:
                nx, ny = cx + self.DIR_MAP[d][0], cy + self.DIR_MAP[d][1]
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
                    d = random.choice([self.NORTH, self.SOUTH, self.EAST, self.WEST])
                    nx, ny = x + self.DIR_MAP[d][0], y + self.DIR_MAP[d][1]
                    if 0 <= nx < self.width and 0 <= ny < self.height and (nx, ny) not in self.reserved:
                        self.carve_wall(x, y, d)
        
        if step_callback:
            step_callback('gen_done', None, None)

    def solve(self, start_pt: Tuple[int, int], end_pt: Tuple[int, int], step_callback=None) -> str:
        queue = deque([(start_pt, "")])
        visited = {start_pt}

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
                    nx, ny = cx + self.DIR_MAP[d][0], cy + self.DIR_MAP[d][1]
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        if (nx, ny) not in visited:
                            visited.add((nx, ny))
                            queue.append(((nx, ny), path + self.DIR_STR[d]))

        if step_callback:
            step_callback('solve_done', None, None)
        return ""

    def save(self, filepath: str, entry: Tuple[int, int], exit_pt: Tuple[int, int], path_str: str):
        with open(filepath, 'w') as f:
            for row in self.grid:
                f.write("".join(f"{cell:X}" for cell in row) + "\n")
            f.write("\n")
            f.write(f"{entry[0]},{entry[1]}\n")
            f.write(f"{exit_pt[0]},{exit_pt[1]}\n")
            f.write(f"{path_str}\n")

    def get_grid(self) -> List[List[int]]:
        return self.grid
