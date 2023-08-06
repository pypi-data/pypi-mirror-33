#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `dt_test` package."""


import unittest
from click.testing import CliRunner

from dt_test import dt_test
from dt_test import cli


class TestDt_test(unittest.TestCase):
    """Tests for `dt_test` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'dt_test.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
