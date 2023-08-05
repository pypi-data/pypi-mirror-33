#!/usr/bin/env python3
# -*- coding: utf-8 -*- #

import unittest
from twsecli import cli

import click
from click.testing import CliRunner


class TestAlignmentFunction(unittest.TestCase):
  """ TestAlignmentFunction """
  def test_alignment(self):
    self.assertEqual(cli.alignment('中文', 4), '中文')
    self.assertEqual(cli.alignment('中文', 6), '中文  ')

  def test_alignment_digit(self):
    self.assertEqual(cli.alignment('中文1', 6), '中文1 ')
    self.assertEqual(cli.alignment('中12', 6), '中12  ')

  def test_alignment_alphabet(self):
    self.assertEqual(cli.alignment('中文a', 6), '中文a ')
    self.assertEqual(cli.alignment('中ab', 6), '中ab  ')


class TestColoredFunction(unittest.TestCase):
  """ TestColoredFunction """
  def test_colored(self):
    self.assertEqual(cli.colored('綠色', 'green'), '\033[1;32m綠色\033[m')
    self.assertEqual(cli.colored('紅色', 'red'), '\033[1;31m紅色\033[m')


class TestCliFunction(unittest.TestCase):
  """ TestCliFunction """
  def test_cli(self):
    runner = CliRunner()
    result = runner.invoke(cli.cli, ['1234', '5678'])
    self.assertEqual(result.exit_code, 0)


if __name__ == '__main__':
  unittest.main()
