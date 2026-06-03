import sys
import os
from typing import Dict, Any
import random

from mazegen.generator import MazeGenerator


def parse_config(path: str) -> Dict[str, Any]:
    config: Dict[str, str] = {}
    try:
        with open(path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                if '=' not in line:
                    print(f"Error: Syntax error on line {line_num}: '{line}'")
                    sys.exit(1)

                key, value = line.split('=', 1)
                config[key.strip().upper()] = value.strip()

        required = ["WIDTH",
                    "HEIGHT",
                    "ENTRY",
                    "EXIT",
                    "OUTPUT_FILE",
                    "PERFECT",
                    ]

        for req in required:
            if req not in config:
                print(f"Error: Mandatory key '{req}' is missing from config.")
                sys.exit(1)

        return config
    except FileNotFoundError:
        print(f"Error: Config file '{path}' not found.")
        sys.exit(1)


def get_validated_config(raw_config: Dict[str, Any]) -> Dict[str, Any]:
    try:
        width = int(raw_config['WIDTH'])
        height = int(raw_config['HEIGHT'])

        if width <= 0:
            print("Error: WIDTH must be a positive integer.")
            sys.exit(1)

        if height <= 0:
            print("Error: HEIGHT must be a positive integer.")
            sys.exit(1)

        entry_raw = raw_config['ENTRY'].split(',')
        exit_raw = raw_config['EXIT'].split(',')

        if len(entry_raw) != 2 or len(exit_raw) != 2:
            print("Error: ENTRY and EXIT must have exactly 2 coordinates.")

            sys.exit(1)

        entry = (int(entry_raw[0].strip()), int(entry_raw[1].strip()))
        exit_point = (int(exit_raw[0].strip()), int(exit_raw[1].strip()))

        if not (0 <= entry[0] < width and 0 <= entry[1] < height):
            print("Error: Entry coordinates are out of maze bounds.")
            sys.exit(1)

        if not (0 <= exit_point[0] < width and 0 <= exit_point[1] < height):
            print("Error: Exit coordinates are out of maze bounds.")
            sys.exit(1)

        if entry == exit_point:
            print("Error: Entry and exit coordinates must be different.")
            sys.exit(1)

        pat_w = len(MazeGenerator.PATTERN_42[0])
        pat_h = len(MazeGenerator.PATTERN_42)
        reserved = set()
        if width >= pat_w + 4 and height >= pat_h + 4:
            ox = (width - pat_w) // 2
            oy = (height - pat_h) // 2
            for r in range(pat_h):
                for c in range(pat_w):
                    if MazeGenerator.PATTERN_42[r][c] in ('1', 'X'):
                        reserved.add((ox + c, oy + r))

        if entry in reserved:
            print("Error: Entry coordinates are inside the '42' logo area.")
            sys.exit(1)
        if exit_point in reserved:
            print("Error: Exit coordinates are inside the '42' logo area.")
            sys.exit(1)

        perfect_val = raw_config['PERFECT'].lower()
        if perfect_val not in ['true', 'false', '1', '0', 'yes', 'no']:
            print("Error: PERFECT must be True or False.")
            sys.exit(1)

        seed = int(raw_config.get('SEED', random.randint(1, 1_000_000)))

        display = raw_config.get('DISPLAY', 'ascii').lower()
        if display not in ['ascii', 'mlx']:
            print("Error: DISPLAY must be 'ascii' or 'mlx'.")
            sys.exit(1)

        output_dir = os.path.dirname(raw_config['OUTPUT_FILE'])
        if output_dir and not os.path.exists(output_dir):
            print(f"Error: Output directory '{output_dir}' does not exist.")
            sys.exit(1)

        return {
            "width": width,
            "height": height,
            "entry": entry,
            "exit": exit_point,
            "perfect": raw_config['PERFECT'].lower() in ['true', '1', 'yes'],
            "output": raw_config['OUTPUT_FILE'],
            "seed": seed,
            "display": display,
        }

    except (ValueError, IndexError):
        print("Error: Invalid data format in configuration file.")
        sys.exit(1)
