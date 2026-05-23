import sys
import random
from mazegen.parsing import parse_config, get_validated_config
from mazegen.generator import MazeGenerator
from mazegen.renderer import MazeRenderer


def _reserved_42_cells(width: int, height: int) -> set[tuple[int, int]]:
    pat_w = len(MazeGenerator.PATTERN_42[0])
    pat_h = len(MazeGenerator.PATTERN_42)
    if width < pat_w + 4 or height < pat_h + 4:
        return set()

    ox = (width - pat_w) // 2
    oy = (height - pat_h) // 2

    reserved: set[tuple[int, int]] = set()
    for r in range(pat_h):
        for c in range(pat_w):
            if MazeGenerator.PATTERN_42[r][c] in ("1", "X"):
                reserved.add((ox + c, oy + r))
    return reserved


def _nearest_free_cell(
    start: tuple[int, int],
    *,
    width: int,
    height: int,
    reserved: set[tuple[int, int]],
    avoid: set[tuple[int, int]] | None = None,
) -> tuple[int, int]:
    avoid = avoid or set()

    x0, y0 = start
    x0 = min(max(x0, 0), width - 1)
    y0 = min(max(y0, 0), height - 1)

    # BFS by Manhattan distance (guarantees nearest in steps).
    from collections import deque

    q = deque([(x0, y0)])
    seen = {(x0, y0)}
    while q:
        x, y = q.popleft()
        if (x, y) not in reserved and (x, y) not in avoid:
            return (x, y)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in seen:
                seen.add((nx, ny))
                q.append((nx, ny))

    raise ValueError("No valid cell available for entry/exit.")


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        sys.exit(1)

    raw_data = parse_config(sys.argv[1])
    conf = get_validated_config(raw_data)

    first_run = [True]

    def factory(new_width=None, new_height=None):
        if new_width is not None:
            conf['width'] = new_width
        if new_height is not None:
            conf['height'] = new_height
  
        reserved = _reserved_42_cells(conf["width"], conf["height"])

        conf["entry"] = _nearest_free_cell(
            conf["entry"],
            width=conf["width"],
            height=conf["height"],
            reserved=reserved,
        )
        conf["exit"] = _nearest_free_cell(
            conf["exit"],
            width=conf["width"],
            height=conf["height"],
            reserved=reserved,
            avoid={conf["entry"]},
        )

        seed = conf['seed'] if first_run[0] else random.randint(1, 1000000)
        first_run[0] = False

        maze = MazeGenerator(
            width=conf['width'],
            height=conf['height'],
            seed=seed
        )

        maze.stamp_42()
        return maze, conf['entry'], conf['exit'], conf['perfect'], conf['output']

    renderer = MazeRenderer(factory)
    renderer.run()


if __name__ == "__main__":
    main()
