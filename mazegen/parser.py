"""
Configuration file parsing and validation
parser(path) is the single public entry: it reads the file, validates
every field, and loads the result into :class:Config.  The lower-level
read_pairs and validate helpers stay importable for tests or custom
pipelines
Config file format, one KEY=VALUE per line, # lines are comments:

    WIDTH=20
    HEIGHT=15
    ENTRY=0,0
    EXIT=19,14
    OUTPUT_FILE=maze.txt
    PERFECT=True
    SEED=42          # optional
    ANIMATE=True     # optional

Keys are case-insensitive, SEED and ANIMATE are optional
"""

import os
from typing import Dict, Optional, Tuple
from .config import Config
from . import pattern

_REQUIRED = ("WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT")
_TRUE = ("true", "1", "yes")
_FALSE = ("false", "0", "no")
_MIN_SIDE = 11


class ConfigError(Exception):
    """Raised when the configuration file is missing, malformed, or invalid"""


def read_pairs(path: str) -> Dict[str, str]:
    """
    Read path into a dict of raw KEY: value strings

    Blank lines and # comments are skipped.  Keys are upper-cased

    Args:
        path: Path to the configuration file

    Returns:
        Dict of raw string values keyed by upper-cased key

    Raises:
        ConfigError: On a missing file, a line without =, or a missing
            mandatory key
    """
    pairs: Dict[str, str] = {}
    try:
        with open(path, "r") as file:
            for number, raw in enumerate(file, 1):
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    raise ConfigError(
                        f"Syntax error on line {number}: {line!r} "
                        "(expected KEY=VALUE)."
                    )
                key, value = line.split("=", 1)
                # Drop any trailing inline comment (everything after a #)
                value = value.split("#", 1)[0]
                pairs[key.strip().upper()] = value.strip()
    except FileNotFoundError:
        raise ConfigError(f"Config file {path!r} not found.")

    for key in _REQUIRED:
        if key not in pairs:
            raise ConfigError(f"Mandatory key {key!r} is missing.")
    return pairs


def _to_int(name: str, text: str) -> int:
    """Parse text into an int or raise a ConfigError naming the field"""
    try:
        return int(text)
    except ValueError:
        raise ConfigError(f"{name} must be a whole number, not {text!r}.")


def _to_coord(name: str, text: str) -> Tuple[int, int]:
    """Parse an x,y pair into a tuple or raise a ConfigError"""
    parts = text.split(",")
    if len(parts) != 2:
        raise ConfigError(f"{name} must be two values 'x,y', not {text!r}.")
    return _to_int(name, parts[0].strip()), _to_int(name, parts[1].strip())


def _to_bool(name: str, text: str) -> bool:
    """Parse a boolean string or raise a ConfigError listing valid forms"""
    low = text.lower()
    if low in _TRUE:
        return True
    if low in _FALSE:
        return False
    raise ConfigError(
        f"{name} must be one of {_TRUE + _FALSE}, not {text!r}."
    )


def validate(pairs: Dict[str, str]) -> None:
    """
    Validate raw config strings and return typed, checked values.

    Args:
        pairs: Dict produced by :func:read_pairs.

    Returns:
        Dict with typed keys ready for Config.load(result):
        width, height, entry, exit, perfect, output, animate, seed.

    Raises:
        ConfigError: On any out-of-range, malformed, or contradictory value.
    """

    # Width and height
    width = _to_int("WIDTH", pairs["WIDTH"])
    height = _to_int("HEIGHT", pairs["HEIGHT"])

    if width <= 1 or height <= 1:
        raise ConfigError(
            f"WIDTH and HEIGHT must each be >= {_MIN_SIDE} "
            f"(got {width}x{height})."
        )

    # Entry and exit
    entry = _to_coord("ENTRY", pairs["ENTRY"])
    exit_pt = _to_coord("EXIT", pairs["EXIT"])

    if not (0 <= entry[0] < width and 0 <= entry[1] < height):
        raise ConfigError("ENTRY is outside the maze bounds.")

    if not (0 <= exit_pt[0] < width and 0 <= exit_pt[1] < height):
        raise ConfigError("EXIT is outside the maze bounds.")

    if entry == exit_pt:
        raise ConfigError("ENTRY and EXIT must be different cells.")

    reserved = pattern.reserved_cells(width, height)
    if entry in reserved:
        raise ConfigError("ENTRY falls inside the '42' logo area.")

    if exit_pt in reserved:
        raise ConfigError("EXIT falls inside the '42' logo area.")

    # Output file
    output = pairs["OUTPUT_FILE"]
    out_dir = os.path.dirname(output)
    if out_dir and not os.path.isdir(out_dir):
        raise ConfigError(f"Output directory {out_dir!r} does not exist.")

    # Perfect and Animation
    perfect = _to_bool("PERFECT", pairs["PERFECT"])
    animate = _to_bool("ANIMATE", pairs["ANIMATE"]) if "ANIMATE" in pairs \
        else True

    # 42 pattern
    pat: Optional[int] = None
    if "PATTERN" in pairs:
        pat = _to_int("PATTERN", pairs["PATTERN"])
        if pat not in [1, 2, 3, 4, 5]:
            raise ConfigError("Invalid pattern, expected 1, 2, 3, 4 or 5")

    # Seed
    seed: Optional[int] = None
    if "SEED" in pairs:
        seed = _to_int("SEED", pairs["SEED"])
        if seed < 0:
            raise ConfigError(f"SEED must be >= 0, not {seed}.")

    Config.load(
        width, height, entry, exit_pt,
        perfect, output, animate, seed,
        pat
    )


def parser(path: str) -> None:
    """
    Parse, validate, and load the config file at path into class Config

    This is the one call needed to set up configuration.  After it returns,
    every Config attribute is populated and a seed is guaranteed

    Args:
        path: Path to the configuration file

    Raises:
        ConfigError: On any parsing or validation failure, Callers should
            catch this and print a clean message instead of crashing
    """
    validate(read_pairs(path))
