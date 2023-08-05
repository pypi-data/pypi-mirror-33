# -*- coding: utf-8 -*-

"""Main module."""

import argparse
import sys


def ingredients(amount: int = 1) -> None:
    """
    Prints out the ingredients needed to make batch(es) of pancakes!

    See https://stackoverflow.com/questions/18275023/dont-show-long-options-twice-in-print-help-from-argparse
    for other information on argparse that shows more details on how to work with argparse.
    """

    print(f"{amount} cup of flour")
    print(f"{amount} pinch of salt")
    print(f"± {amount} cup of water")
    print(f"{amount} egg")
    print(f"{amount} teaspoon of baking powder")
    print(f"± {amount} cup of milk")
    print(f"\nMix ingredients together well")
    print(f"Texture of a thin bechamel")
    print(f"\nPour 1 ladle of mixture into a medium-hot pancake pan")
    print(f"Tilt pan to distribute a thin layer evenly over the surface")
    print(f"Turn after 1 minute")


def parse_pancakes(args_parm=None):
    parser = argparse.ArgumentParser(description=f"""Prints out the recipe and the ingredients needed to make 
                                                     pancakes depending on the number desired!""")
    parser.add_argument('-dnp', '--pancakes',
                        help="number of pancakes desired",
                        type=int,
                        default=1)
    results = parser.parse_args(args_parm)
    return results.pancakes


if __name__ == "__main__":
    args = parse_pancakes(sys.argv[1:])
    print(f"args: {args}")
    ingredients(args)
