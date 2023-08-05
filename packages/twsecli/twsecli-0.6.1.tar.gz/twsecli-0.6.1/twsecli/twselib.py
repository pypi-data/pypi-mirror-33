#!/usr/bin/env python3
# -*- coding: utf-8 -*- #

import time
import requests


"""
twse official website
http://mis.twse.com.tw

twse API information
https://github.com/Asoul/tsrtc
"""


class TWSELIB(object):

  def __init__(self):
    self.timestamp = int(time.time() * 1000)
    self.headers = {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
      'Content-Type': 'text/html; charset=UTF-8',
      'Accept-Language': 'zh-TW'
    }
    self.__req = self.get_cookie()
    pass

  def get_cookie(self):
    api_get_stock_cookie = 'http://mis.twse.com.tw/stock/index.jsp'
    req = requests.Session()
    req.headers.update(self.headers)
    req.get(api_get_stock_cookie)
    return req

  def get_stock_key(self, stock_symbol):
    api_get_stock = "http://mis.twse.com.tw/stock/api/getStock.jsp"
    payload = {
      'json': 1,
      '_': self.timestamp,
      'ch': '{}.tw'.format(stock_symbol)
    }
    res = self.__req.get(api_get_stock, params=payload)
    try:
      if res.json()['msgArray'][0]['key']:
        return res.json()['msgArray'][0]['key']
    except IndexError as err:
      print("Index error: {}".format(err))
      return ''

  def get_stock_info(self, stock_keys):
    api_get_stock_info = "http://mis.twse.com.tw/stock/api/getStockInfo.jsp"
    payload = {
      'json': 1,
      '_': self.timestamp,
      'delay': 0,
      'ex_ch': '%7C'.join(stock_keys)
    }
    for _ in range(3):
      try:
        res = self.__req.get(api_get_stock_info, params=payload)
        if res.json()['msgArray']:
          return res.json()['msgArray']
      except KeyError as err:
        print("Key error: {}, auto retry after 3 seconds...".format(err))
        time.sleep(3)
        self.__req = self.get_cookie()
    print("Temporary failed, please try later.")
    return []
