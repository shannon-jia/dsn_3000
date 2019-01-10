#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `dsn_3000` package."""


import unittest
from click.testing import CliRunner

from dsn_3000 import dsn_3000
from dsn_3000 import cli


class TestDsn_3000(unittest.TestCase):
    """Tests for `dsn_3000` package."""

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
        assert 'dsn_3000.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
