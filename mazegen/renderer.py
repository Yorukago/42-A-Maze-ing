import sys
import os
import time
from .generator import MazeGenerator

# Available Colors (Name, ANSI Code, Complement ANSI Code)
COLORS = {
    '1': ('Pink',    '\033[38;5;213m', '\033[38;5;118m'), # Pink -> Light Green
    '2': ('Gray',    '\033[38;5;250m', '\033[38;5;208m'), # Gray -> Orange
    '3': ('Red',     '\033[38;5;196m', '\033[38;5;51m'),  # Red -> Cyan
    '4': ('Green',   '\033[38;5;46m',  '\033[38;5;201m'), # Green -> Magenta
    '5': ('Blue',    '\033[38;5;27m',  '\033[38;5;226m'), # Blue -> Yellow
    '6': ('Cyan',    '\033[38;5;51m',  '\033[38;5;196m'), # Cyan -> Red
    '7': ('Magenta', '\033[38;5;201m', '\033[38;5;46m'),  # Magenta -> Green
    '8': ('Yellow',  '\033[38;5;226m', '\033[38;5;27m'),  # Yellow -> Blue
    '9': ('White',   '\033[38;5;231m', '\033[38;5;201m')  # White -> Magenta
}
RESET = "\033[0m"
ENTRY_EXIT_COLOUR = "\033[38;5;204m"

BOX_CHARS = {
    0: ' ',
    1: '╵', 2: '╶', 3: '└',
    4: '╷', 5: '│', 6: '┌', 7: '├',
    8: '╴', 9: '┘', 10: '─', 11: '┴',
    12: '┐', 13: '┤', 14: '┬', 15: '┼'
}

def get_path_coords(start, path_str):
    coords = []
    x, y = start
    for d in path_str:
        if d == 'N': y -= 1
        elif d == 'S': y += 1
        elif d == 'E': x += 1
        elif d == 'W': x -= 1
        coords.append((x, y))
    return coords

class MazeRenderer:
    def __init__(self, generator_factory):
        self.factory = generator_factory 
        self.anim_state = None
        self.anim_active_cell = None
        self.anim_visited = None
        self.show_path = False
        
        # Default to Gray walls and Pink path
        self.wall_col = COLORS['2'][1] 
        self.path_col = COLORS['1'][1]
        self.pattern_col = COLORS['2'][2]
        
        os.system('clear')
        
        self.generate_and_solve()
        
    def generate_and_solve(self, new_width=None, new_height=None):
        self.maze, self.entry, self.exit_pt, perfect, output_file = self.factory(new_width, new_height)
        self.path_str = ""
        self.path_coords = []
        
        self.maze.generate(self.entry, perfect=perfect, step_callback=self.on_step)
        self.path_str = self.maze.solve(self.entry, self.exit_pt, step_callback=self.on_step)
        self.path_coords = get_path_coords(self.entry, self.path_str)
        
        self.maze.save(output_file, self.entry, self.exit_pt, self.path_str)
        
    def on_step(self, state, active_cell, visited):
        self.anim_state = state
        self.anim_active_cell = active_cell
        if visited is not None:
            self.anim_visited = visited
            
        if state == 'gen':
            self.render()
            time.sleep(0.01)
        elif state == 'solve':
            self.render()
            time.sleep(0.005)
        elif state == 'gen_done' or state == 'solve_done':
            self.anim_state = None
            self.anim_active_cell = None
            self.anim_visited = None
            self.render()

    def _has_v_wall(self, vx, y):
        if y < 0 or y >= self.maze.height: return False
        if vx == 0:
            return bool(self.maze.grid[y][0] & MazeGenerator.WEST)
        if vx == self.maze.width:
            return bool(self.maze.grid[y][vx-1] & MazeGenerator.EAST)
        return bool(self.maze.grid[y][vx] & MazeGenerator.WEST)

    def _has_h_wall(self, x, vy):
        if x < 0 or x >= self.maze.width: return False
        if vy == 0:
            return bool(self.maze.grid[0][x] & MazeGenerator.NORTH)
        if vy == self.maze.height:
            return bool(self.maze.grid[vy-1][x] & MazeGenerator.SOUTH)
        return bool(self.maze.grid[vy][x] & MazeGenerator.NORTH)

    def _is_pattern_cell(self, x, y):
        if x < 0 or x >= self.maze.width or y < 0 or y >= self.maze.height:
            return False
        return (x, y) in self.maze.reserved

    def _vertex_color(self, vx, vy):
        if (self._is_pattern_cell(vx-1, vy-1) or 
            self._is_pattern_cell(vx, vy-1) or 
            self._is_pattern_cell(vx-1, vy) or 
            self._is_pattern_cell(vx, vy)):
            return self.pattern_col
        return self.wall_col

    def render(self):
        sys.stdout.write('\033[H') 
        
        w = self.maze.width
        h = self.maze.height
        lines = []
        
        for vy in range(h + 1):
            r1 = ""
            for vx in range(w + 1):
                N = self._has_v_wall(vx, vy-1)
                S = self._has_v_wall(vx, vy)
                E = self._has_h_wall(vx, vy)
                W = self._has_h_wall(vx-1, vy)
                mask = (1 if N else 0) | (2 if E else 0) | (4 if S else 0) | (8 if W else 0)
                
                v_char = BOX_CHARS[mask]
                v_col = self._vertex_color(vx, vy)
                r1 += v_col + v_char + RESET
                
                if vx < w:
                    has_h = self._has_h_wall(vx, vy)
                    edge_col = self.pattern_col if (self._is_pattern_cell(vx, vy-1) or self._is_pattern_cell(vx, vy)) else self.wall_col
                    if has_h:
                        r1 += edge_col + "───" + RESET
                    else:
                        r1 += "   "
            lines.append(r1)
            
            if vy < h:
                r2 = ""
                for vx in range(w + 1):
                    has_v = self._has_v_wall(vx, vy)
                    edge_col = self.pattern_col if (self._is_pattern_cell(vx-1, vy) or self._is_pattern_cell(vx, vy)) else self.wall_col
                    if has_v:
                        r2 += edge_col + "│" + RESET
                    else:
                        r2 += " "
                    
                    if vx < w:
                        center_str = "   "
                        if (vx, vy) == self.entry:
                            center_str = f" {ENTRY_EXIT_COLOUR}█{RESET} "
                        elif (vx, vy) == self.exit_pt:
                            center_str = f" {ENTRY_EXIT_COLOUR}█{RESET} "
                        elif self.show_path and self.anim_state is None and (vx, vy) in self.path_coords and (vx, vy) != self.entry and (vx, vy) != self.exit_pt:
                            center_str = f" {self.path_col}•{RESET} "
                        elif self.anim_state == 'solve' and self.anim_visited and (vx, vy) in self.anim_visited:
                            center_str = f" {self.path_col}░{RESET} "
                        
                        if self.anim_active_cell == (vx, vy):
                            if self.anim_state == 'gen':
                                center_str = f" {self.path_col}G{RESET} "
                            elif self.anim_state == 'solve':
                                center_str = f" {self.path_col}S{RESET} "
                                
                        r2 += center_str
                lines.append(r2)

        for l in lines:
            sys.stdout.write(l + "\033[K\n")
            
    def run(self):
        while True:
            self.render()
            print()
            print("=== A-Maze-Ing Controls ===")
            print("1. Re-generate a new maze")
            print("2. Show path")
            print("3. Change maze size")
            print("4. Change colors")
            print("5. Quit\n")
            
            try:
                ch = input("Choice? (1-5): ").strip()
            except (KeyboardInterrupt, EOFError):
                break
                
            if ch == '5' or ch.lower() == 'q':
                break
            elif ch == '1':
                os.system('clear')
                self.generate_and_solve()
            elif ch == '2':
                self.show_path = not self.show_path
            elif ch == '3':
                try:
                    nw = int(input("New width (min 10): "))
                    nh = int(input("New height (min 10): "))
                    if nw >= 10 and nh >= 10:
                        os.system('clear')
                        self.generate_and_solve(new_width=nw, new_height=nh)
                    else:
                        print("Size too small! Please enter values >= 10.")
                        time.sleep(1)
                except ValueError:
                    print("Invalid number!")
                    time.sleep(1)
            elif ch == '4':
                print("\n--- Available Colors ---")
                for k, v in COLORS.items():
                    print(f"{k}. {v[0]}")
                try:
                    p = input("Select primary wall color (1-9): ").strip()
                    s = input("Select secondary path color (1-9): ").strip()
                    if p in COLORS and s in COLORS:
                        self.wall_col = COLORS[p][1]
                        self.path_col = COLORS[s][1]
                        self.pattern_col = COLORS[p][2]
                    else:
                        print("Invalid selection!")
                        time.sleep(1)
                except (KeyboardInterrupt, EOFError, ValueError):
                    pass
                os.system('clear')
        os.system('clear')
