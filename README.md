*This project has been created as part of the 42 curriculum by jzorreta, ljeronim.*

# A-Maze-ing

## Description

A-Maze-ing is a maze generator and visualiser written in Python. It reads a
plain-text configuration file, generates a maze (optionally perfect), writes it
to a hexadecimal wall-encoded output file, and displays it in an interactive
ASCII terminal renderer that animates the build and the solve.

The maze is built with the recursive backtracker (depth-first search) and
solved with breadth-first search. A "42" logo is reserved in the centre of the
maze whenever the size allows it. The generation logic lives in a small,
self-contained `mazegen` package that can be installed with `pip` and reused by
other projects.

## Instructions

Requirements: Python 3.10 or later.

```bash
make venv        # create a virtual environment in .venv
make install     # install build and lint dependencies
make run         # run with the default config.txt
```

Run manually:

```bash
python3 a_maze_ing.py config.txt
```

Other Make targets:

```bash
make lint        # flake8 + mypy (project standard)
make lint-strict # flake8 + mypy --strict
make build       # build mazegen-1.0.0 (.whl and .tar.gz) at the repo root
make debug       # run under pdb
make clean       # remove caches and build artifacts
```

Interactive controls (terminal renderer):

| Key | Action                                  |
|-----|------------------------------------------|
| 1   | Re-generate a new maze (new seed)        |
| 2   | Show / hide the shortest path            |
| 3   | Change maze size                         |
| 4   | Change wall and path colours             |
| 5   | Toggle the build/solve animation on/off  |
| 6   | Quit                                     |

## Configuration file

One `KEY=VALUE` per line. Lines starting with `#` are comments, and an inline
`#` after a value is ignored too. Keys are case-insensitive.

| Key           | Required | Meaning                                  | Example              |
|---------------|----------|-------------------------------------------|----------------------|
| `WIDTH`       | yes      | Maze width in cells (>= 11)               | `WIDTH=21`           |
| `HEIGHT`      | yes      | Maze height in cells (>= 11)              | `HEIGHT=21`          |
| `ENTRY`       | yes      | Entry cell `x,y`                          | `ENTRY=0,0`          |
| `EXIT`        | yes      | Exit cell `x,y`                           | `EXIT=20,20`         |
| `OUTPUT_FILE` | yes      | Output file path                          | `OUTPUT_FILE=maze.txt` |
| `PERFECT`     | yes      | Perfect maze? `True`/`False`              | `PERFECT=False`      |
| `SEED`        | no       | Seed for reproducibility (random if omitted) | `SEED=42`        |
| `ANIMATE`     | no       | Play the animation? `True`/`False` (default True) | `ANIMATE=True` |

Booleans accept `True/False`, `1/0`, or `yes/no`. Entry and exit must be inside
the maze, different from each other, and not inside the reserved "42" cells.

### Output file format

The output file encodes each cell as one hexadecimal digit (a set bit means a
wall is present):

```
bit 0 (1) = North    bit 1 (2) = East    bit 2 (4) = South    bit 3 (8) = West
```

The file contains `HEIGHT` rows of `WIDTH` hex digits, a blank line, then the
entry coordinates, the exit coordinates, and the shortest path as `N`/`E`/`S`/`W`
letters. Every line ends with `\n`.

## Maze generation algorithm

Generation uses the **recursive backtracker** (a depth-first search carving):
starting from the entry cell, it repeatedly moves to a random unvisited
neighbour, knocking down the wall between them, and backtracks when it hits a
dead end. Solving uses **breadth-first search**, which returns the shortest
path.

For an imperfect maze (`PERFECT=False`), extra walls are opened after carving.
A second route to the exit is guaranteed by opening a wall between two
non-adjacent cells of the current solution (such a wall must be closed, or BFS
would already have used the shortcut). A few more interior walls are then opened
for variety, with a guard that never creates a 3x3 fully-open area.

### Why this algorithm

The recursive backtracker is simple to implement iteratively (an explicit
stack, no recursion-depth limits), always produces a fully-connected perfect
maze in a single pass, and tends to make long, winding corridors that look good.
BFS is the natural partner for the shortest-path requirement. Both are easy to
instrument: recording each visited cell as a step is what lets the renderer
replay the animation without ever rebuilding the maze.

## Reusable module (`mazegen`)

The generator is packaged as `mazegen`, installable with `pip`. The public API
is three names: `parser`, `generator`, and `Config`.

```python
from mazegen import parser, generator, Config

parser("config.txt")     # parse + validate into Config, pick a seed
result = generator()     # build + solve + write Config.output

result.grid              # 2D list of 4-bit wall masks
result.solution          # "SSEE..." shortest path
result.entry, result.exit
```

Custom parameters without a file:

```python
from mazegen import generator, Config

Config.load(width=25, height=25, entry=(0, 0), exit=(24, 24),
            perfect=False, output="maze.txt", animate=False, seed=123)
result = generator(save=False)   # don't write a file
```

`generator()` returns a `MazeResult` with `grid`, `entry`, `exit`, `solution`,
`steps` (the recorded animation frames), and `reserved` (the "42" cells). The
exposed grid is the live structure; the hex output file is a separate
serialisation written by `generator(save=True)`.

To rebuild the package from source:

```bash
make build       # produces mazegen-1.0.0-py3-none-any.whl and .tar.gz
```

What is reusable, and how: the entire `mazegen` package (parsing, config,
pattern maths, generation, solving, and serialisation) is independent of the
renderer and the entry point. Any project can `pip install mazegen` and call
`parser`/`generator`/`Config` — the renderer is just one consumer of the
`MazeResult` it returns.

## Project structure

```
a_maze_ing.py        Entry point (uses only parser, generator, Config)
renderer.py          Interactive ASCII renderer (replays MazeResult.steps)
config.txt           Default configuration
mazegen/
  __init__.py        Public API: parser, generator, Config (+ result types)
  parser.py          parser(): read + validate + load Config
  config.py          Config: shared settings store
  generator.py       generator(): build + solve + save; MazeGenerator, MazeResult
  pattern.py         The "42" logo and its placement maths
  README.md          Reusable-module documentation
Makefile, pyproject.toml, requirements.txt
```

## Resources

- Jamis Buck, *Mazes for Programmers* — recursive backtracker and other
  algorithms.
- Wikipedia: "Maze generation algorithm" and "Breadth-first search".
- Python docs: `collections.deque`, `random.Random`, `dataclasses`.

### Use of AI

AI was used as an assistant for the refactor of an earlier working version:
reorganising the package into one-responsibility modules, decoupling the
animation (recording steps into a list instead of a live callback so the maze is
built only once), tightening the imperfect-maze logic to guarantee a second
route, and reviewing for flake8/mypy compliance. Every change was read,
tested, and is explainable by the team; the maze algorithms themselves and the
original renderer were our own work.

## Team and project management

- **jzorreta** — maze generation and solving, package structure, output format.
- **ljeronim** — configuration parsing/validation, renderer.

Planning: we started from the config parser and the bitmask data model, then the
generator, then the renderer, and finally the reusable-package build. The
initial version worked but grew tangled (the renderer rebuilt mazes itself to
animate). The main evolution was the refactor that split each concern into its
own module and made the renderer replay recorded steps. What worked well: the
class-level `Config` made state easy to share; BFS gave the shortest path for
free. What could improve: a key-by-key input loop for the renderer instead of a
numbered menu, and more generation algorithms. Tools used: git, flake8, mypy,
and the MLX reference material from the subject.
