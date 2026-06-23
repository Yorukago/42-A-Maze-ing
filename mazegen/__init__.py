from .config import Config
from .parser import parser, ConfigError
from . import pattern
from .generator import (
    generator,
    MazeResult,
    nearest_free,
    Step,
    NORTH,
    EAST,
    SOUTH,
    WEST
)

__name__ = "mazegen"
__version__ = "1.0.0"
__author__ = "jzorreta, ljeronim"

__all__ = [
    "parser",
    "generator",
    "Config",
    "ConfigError",
    "MazeResult",
    "nearest_free",
    "Step",
    "NORTH",
    "EAST",
    "SOUTH",
    "WEST",
    "pattern"
]
