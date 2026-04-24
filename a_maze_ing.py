import sys
from src.parsing import parse_config, get_validated_config
from maze.src.generator import MazeGenerator


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        sys.exit(1)

    # Parse & Validate
    raw_data = parse_config(sys.argv[1])
    conf = get_validated_config(raw_data)

    # Initialize Generator
    maze = MazeGenerator(
        width=conf['width'],
        height=conf['height'],
        seed=conf['seed']
    )

    # Mandatory 42 Stamp (implememnt on mazegen thing)
    # maze.stamp_42()

    # Generate & Save
    # maze.generate(conf['entry'])

    # Printing success test
    print(f"Successfully initialized {maze.width}x{maze.height} maze.")
    print(f"Entry: {conf['entry']} | Exit: {conf['exit']}")


if __name__ == "__main__":
    main()
