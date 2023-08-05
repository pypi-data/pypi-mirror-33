#!/usr/bin/env python3
# -*- coding: utf-8 -*- #

import unittest
from twsecli import twselib


class TestTWSELIB(unittest.TestCase):
  """ TestTWSELIB """
  def setUp(self):
    self.twse_lib = twselib.TWSELIB()

  def tearDown(self):
    del self.twse_lib

  def test_get_cookie(self):
    self.assertIsNotNone(self.twse_lib.get_cookie())

  def test_get_stock_key_tse(self):
    self.assertEqual(self.twse_lib.get_stock_key('0050'), 'tse_0050.tw')

  def test_get_stock_key_otc(self):
    self.assertEqual(self.twse_lib.get_stock_key('5425'), 'otc_5425.tw')

  def test_get_stock_info(self):
    keys = ['tse_0050.tw', 'otc_5425.tw']
    self.assertIsNotNone(self.twse_lib.get_stock_info(keys))


if __name__ == '__main__':
  unittest.main()
