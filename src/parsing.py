import sys
from typing import Dict, Any


def parse_config(path: str) -> Dict[str, Any]:
    """Reads raw key-value pairs from the configuration file"""
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
                    "PERFECT"
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
    """Validates and converts raw config strings into proper Python types"""
    try:
        width = int(raw_config['WIDTH'])
        height = int(raw_config['HEIGHT'])

        entry_raw = raw_config['ENTRY'].split(',')
        exit_raw = raw_config['EXIT'].split(',')

        entry = (int(entry_raw[0]), int(entry_raw[1]))
        exit_point = (int(exit_raw[0]), int(exit_raw[1]))

        if not (0 <= entry[0] < width and 0 <= entry[1] < height):
            print("Error: Entry coordinates are out of maze bounds.")
            sys.exit(1)

        return {
            "width": width,
            "height": height,
            "entry": entry,
            "exit": exit_point,
            "perfect": raw_config['PERFECT'].lower() in ['true', '1', 'yes'],
            "seed": int(raw_config.get('SEED', 0)),
            "output": raw_config['OUTPUT_FILE']
        }
    except (ValueError, IndexError):
        print("Error: Invalid data format in configuration file.")
        sys.exit(1)
