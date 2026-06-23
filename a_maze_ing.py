"""
A-Maze-ing
Wires the three public pieces of the mazegen package together:

    parser(path)  ->  fills Config
    generator()   ->  builds, solves, and saves the maze
    renderer      ->  replays and displays it

Nothing here reaches into package internals, only parser, generator,
and Config are used
"""

import sys
from mazegen import parser, generator, ConfigError


def main() -> None:
    """
    Parse the config given on the command line, build the maze, then display

    On any configuration error a clean message is printed and the program
    exits with status 1 instead of crashing
    """
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py <config.txt>")
        sys.exit(1)

    try:
        parser(sys.argv[1])
    except ConfigError as error:
        print(f"\033[38;2;255;0;111m[ERROR]\033[0m - {error}")
        sys.exit(1)

    result = generator()

    if not result.solution:
        print("Warning: the generated maze has no entry-to-exit path.")

    from renderer import MazeRenderer
    MazeRenderer(result).run()


if __name__ == "__main__":
    main()
