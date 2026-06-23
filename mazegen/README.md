# mazegen

A small, reusable maze generator: builds a maze with the recursive
backtracker (DFS), solves it with breadth-first search (BFS), and writes a
hexadecimal wall-encoded output file. Designed to be imported by other
projects.

## Install

```bash
pip install mazegen-1.0.0-py3-none-any.whl
# or from source
pip install .
```

## Exposed parts

Only three names are needed:

- `parser(path)` — read and validate a config file into `Config`.
- `generator()` — build, solve, and save a maze.
- `Config` — the shared settings store (class-level attributes).

## Basic example

```python
from mazegen import parser, generator, Config

parser("config.txt")        # fills Config and picks a seed
result = generator()        # builds, solves, writes Config.output

print(result.solution)      # "SSEE..." (N/E/S/W letters)
print(result.entry, result.exit)
print(result.grid[0][0])    # wall bitmask of the top-left cell
```

## Custom parameters (without a file)

`Config` can be populated directly, skipping the parser:

```python
from mazegen import generator, Config

Config.load(
    width=25, height=25,
    entry=(0, 0), exit=(24, 24),
    perfect=False, output="maze.txt",
    animate=True, seed=123,        # seed=None -> random
)
result = generator()              # also writes Config.output
```

## Accessing the structure and the solution

`generator()` returns a `MazeResult`:

| Field      | Meaning                                                        |
|------------|----------------------------------------------------------------|
| `grid`     | 2D row-major list; each cell is a 4-bit wall mask.             |
| `entry`    | Resolved `(x, y)` entry cell.                                  |
| `exit`     | Resolved `(x, y)` exit cell.                                   |
| `solution` | Shortest path as `N`/`E`/`S`/`W` letters (`""` if none).       |
| `steps`    | Ordered build-then-solve frames (for animation/replay).       |
| `reserved` | Cells occupied by the `42` logo.                              |

Wall bits (a set bit means a wall is present):

```
NORTH = 1   EAST = 2   SOUTH = 4   WEST = 8
```

These constants are importable: `from mazegen import NORTH, EAST, SOUTH, WEST`.

## Notes

- The grid the module exposes is **not** the same as the hex output file;
  the file is a serialisation written by `generator()`.
- A `42` logo is reserved in the maze centre when the size allows it.
- For an imperfect maze (`perfect=False`) at least two distinct routes from
  entry to exit are guaranteed.
