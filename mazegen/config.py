"""
Central configuration

Config keeps every setting as a class-level attribute, so no instance is
ever needed: the parser fills it once with Config.load(...) and every other
component (generator, renderer, a future importing project) reads the values
straight off the class

The seed is stored here too, When the config file omits SEED the parser
passes seed=None and load rolls a random one, so a run is always
reproducible afterwards (the chosen seed is known and can be reused)
"""

import random
from typing import Optional, Tuple
from .pattern import Pattern


class Config:
    """
    Shared maze configuration.

    Read all attributes directly on the class

    Attributes:
        width:   Maze width in cells
        height:  Maze height in cells
        entry:   (x, y) entry cell
        exit:    (x, y) exit cell
        perfect: True for a perfect maze (one route), False for several
        output:  Path of the hex output file to write
        animate: True to play the build/solve animation, False to skip it
        seed:    Random seed used for generation
    """

    width: int = 0
    height: int = 0
    entry: Tuple[int, int] = (0, 0)
    exit: Tuple[int, int] = (0, 0)
    perfect: bool = True
    output: str = "maze.txt"
    animate: bool = True
    seed: int = 0
    pat: int = 0

    @classmethod
    def load(
        cls,
        width: int,
        height: int,
        entry: Tuple[int, int],
        exit: Tuple[int, int],
        perfect: bool,
        output: str,
        animate: bool,
        seed: Optional[int],
        pat: Optional[int]
    ) -> None:
        """
        Populate every class attribute from already-validated values

        Args:
            width:   Maze width in cells
            height:  Maze height in cells
            entry:   (x, y) entry cell
            exit:    (x, y) exit cell
            perfect: Whether the maze should be perfect
            output:  Output file path
            animate: Whether to animate generation/solving
            seed:    Explicit seed, or None to generate a random one
        """
        cls.width = width
        cls.height = height
        cls.entry = entry
        cls.exit = exit
        cls.perfect = perfect
        cls.output = output
        cls.animate = animate
        cls.seed = seed if seed is not None else cls.new_seed()
        cls.pat = pat if pat is not None else 1
        Pattern.choose_pattern(pat)

    @classmethod
    def new_seed(cls) -> int:
        """
        Generate, store, and return a fresh random seed

        Used when the renderer asks for a brand-new maze: each regeneration is
        different yet still reproducible because the new seed is recorded

        Returns:
            The newly generated seed
        """
        cls.seed = random.randint(1, 1_000_000)
        return cls.seed
