#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ingredients` package."""

import pytest

from click.testing import CliRunner

from ingredients import ingredients
from ingredients import cli


def test_ingredients(capsys):
    """We use the capsys argument to capture printing to stdout."""
    # The ingredients function prints the results, but returns nothing.
    assert ingredients.ingredients(10) == None

    # Capture the result of the ingredients.ingredients() function call.
    captured = capsys.readouterr()

    # If we check captured, we can see that the ingredients have been printed.
    assert "1.0 cups arepa flour" in captured.out
    assert "1.0 cups cheese" in captured.out
    assert "0.25 cups water" in captured.out


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'ingredients.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output
