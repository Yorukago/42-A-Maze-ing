*This project has been created as part of the 42 curriculum by jzorreta, ljeronim.*

# A-Maze-ing

## Description
A-Maze-ing is a Python-based maze generation and visualization tool. The goal of this project is to create a random, perfect (or imperfect) maze and provide a visual representation of it, complete with a solution path and a hidden "42" easter egg pattern. It features an animated interactive ASCII terminal rendering!

## Instructions
1. **Installation**: Ensure you have Python 3.10+ installed.
2. **Setup**: Run `make install` to install dependencies (if any).
3. **Execution**: Run `make run` or `python3 a_maze_ing.py config.txt` to launch the interactive maze generator.
4. **Controls**:
   - `1`: Re-generate a new maze
   - `2`: Show path
   - `3`: Change maze size
   - `4`: Change colors
   - `5`: Quit

## Configuration File Format
The configuration file contains simple key-value pairs separated by `=`. Mandatory keys are:
- `WIDTH` (int): Maze width in cells
- `HEIGHT` (int): Maze height in cells
- `ENTRY` (x,y): Entry coordinates
- `EXIT` (x,y): Exit coordinates
- `OUTPUT_FILE` (string): Filename to save the generated hex grid
- `PERFECT` (bool): Whether the maze is perfect (True) or has loops (False)
- `SEED` (int, optional): Random seed for reproducibility

## Algorithm Choice
We chose the **Recursive Backtracker (Depth-First Search)** algorithm for maze generation.
**Why?** It naturally produces perfect mazes with a unique path, creating long and winding corridors that are visually appealing and challenging. It is easy to implement efficiently using a stack and fully supports seed-based reproducibility.

## Code Reusability
The `mazegen` package is fully reusable! The `MazeGenerator` class inside `src/generator.py` is self-contained.
**How to use:**
```python
from mazegen.src.generator import MazeGenerator

# Initialize a 20x15 maze
maze = MazeGenerator(width=20, height=15, seed=42)
maze.stamp_42()
maze.generate(start_pt=(0,0), perfect=True)
path = maze.solve(start_pt=(0,0), end_pt=(19,14))

# Access the generated structure (2D list of bitmasks)
grid = maze.get_grid()
```

## Resources
- [Wikipedia: Maze generation algorithms](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Astrolog.org: Maze types](http://www.astrolog.org/labyrnth/algrithm.htm)
- **AI Usage**: We used AI assistance to structure the project scaffolding, brainstorm DFS implementation logic, and refine the ANSI terminal rendering interface to ensure good aestethics, subject to change btw

## Team and Project Management
- **Roles**:
  - `jzorreta`: Core algorithm logic and configuration parsing.
  - `ljeronim`: Terminal UI renderer and the most curious person to live in this world
- **Planning**: We initially planned to use Prim's algorithm but pivoted to DFS recursive backtracker mid-project due to the longer, more natural-looking corridors it produces.
- **Pros/Cons**: Pair programming the 42-stamp integration went extremely well. Debugging the bitwise wall carving was challenging but a great learning experience.
- **Tools**: We used `make` for automation, `flake8`/`mypy` for linting, and standard Python libraries.