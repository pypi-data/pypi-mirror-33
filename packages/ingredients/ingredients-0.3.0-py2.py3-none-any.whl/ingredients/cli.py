# -*- coding: utf-8 -*-

"""Console script for ingredients."""
import sys
import click
from ingredients.ingredients import ingredients


@click.command()
@click.argument('count', type=int)
def main(count):
    """Console script for ingredients."""
    ingredients(count)
    return 0


if __name__ == "__main__":

    sys.exit(main(0))  # pragma: no cover
