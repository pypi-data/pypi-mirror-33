# -*- coding: utf-8 -*-

"""Main module."""


def ingredients(count):
    """Prints ingredients for making `count` arepas."""
    print('{:.2} cups arepa flour'.format(0.1 * count))
    print('{:.2} cups cheese'.format(0.1 * count))
    print('{:.2} cups water'.format(0.025 * count))
