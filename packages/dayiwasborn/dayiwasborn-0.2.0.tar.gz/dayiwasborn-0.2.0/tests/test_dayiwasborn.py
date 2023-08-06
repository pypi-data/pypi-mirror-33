#!/usr/bin/env python

"""Tests for `dayiwasborn` package."""

import pytest

from click.testing import CliRunner

from dayiwasborn.dayiwasborn import dayiwasborn
from dayiwasborn import cli


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'dayiwasborn.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output

def test_correct_day_given():
    july_1_2018 = dayiwasborn('name', 2018, 7, 1)
    assert 'Sunday' in july_1_2018

def test_correct_name_given():
    result = dayiwasborn('John', 1900, 1, 1)
    assert 'John' in result
