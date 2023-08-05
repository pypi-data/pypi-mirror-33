#!/usr/bin/env python3
# -*- coding: utf-8 -*- #

import os
import re
import time
import click
from .twselib import TWSELIB


CONTEXT_SETTINGS = {'help_option_names': ['-h', '--help']}
STOCK_CONFIG = os.path.expanduser('~/.config/twsecli/config')


def initial_stock_config(stock_config):
  if not os.path.isfile(stock_config):
    os.makedirs(os.path.dirname(stock_config))
    with open(stock_config, 'w', encoding='utf-8') as f:
      f.write('0050\n')
      f.write('0056\n')
  return stock_config


def alignment(s, space):
  base = len(s)
  count = len(re.findall('[a-zA-Z0-9]', s))
  space = space - (2 * base) + count  # space - ((base - count) * 2) - count
  s = s + (' ' * space)
  return s


def colored(s, color):
  if color == 'green':
    return '\033[1;32m' + s + '\033[m'
  if color == 'red':
    return '\033[1;31m' + s + '\033[m'


def print2terminal(stock_infos):
  if stock_infos:
    print('\n代號  商品          成交   漲跌    幅度    單量    總量   最高   最低   開盤   昨收')
    for stock in stock_infos:
      change = float(stock['z']) - float(stock['y'])
      change_p = change / float(stock['y'])
      stock_name = alignment(stock['n'], 11)
      stock_price = colored('{:>6}'.format(stock['z']), 'red') if change >= 0 else colored('{:>6}'.format(stock['z']), 'green')
      stock_change = colored('{:>+6.2f}'.format(change), 'red') if change >= 0 else colored('{:>+6.2f}'.format(change), 'green')
      stock_change_p = colored('{:>+7.2%}'.format(change_p), 'red') if change >= 0 else colored('{:>+7.2%}'.format(change_p), 'green')
      stock_change_high = colored('{:>6}'.format(stock['h']), 'red') if float(stock['h']) - float(stock['y']) >= 0 else colored('{:>6}'.format(stock['h']), 'green')
      stock_change_low = colored('{:>6}'.format(stock['l']), 'red') if float(stock['l']) - float(stock['y']) >= 0 else colored('{:>6}'.format(stock['l']), 'green')
      stock_change_origin = colored('{:>6}'.format(stock['o']), 'red') if float(stock['l']) - float(stock['y']) >= 0 else colored('{:>6}'.format(stock['o']), 'green')
      print("{:<5} {} {} {} {} {:>7,} {:>7,} {} {} {:>6} {:>6}".format(stock['c'], stock_name, stock_price, stock_change, stock_change_p, int(stock['tv']), int(stock['v']), stock_change_high, stock_change_low, stock_change_origin, stock['y']))
    else:
      print('\n資料時間: {} {}'.format(stock['d'], stock['t']))


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('symbol', nargs=-1)
@click.option('-n', '--interval', default=0, help='seconds to wait between updates, minimum 60s', type=int)
@click.option('-c', '--config', default=initial_stock_config(STOCK_CONFIG), help='stock symbol config, default path ~/.config/twsecli/config', type=click.File('r'))
def cli(config, interval, symbol):
  """
  The twsecil prints real-time stock price.

  You can use stock symbol argument or stock symbol config to control what stock price you want to prints.
  However, if you don't input stock symbol argument, the twsecli will use stock symbol config as default.
  """
  stock_keys = []
  stock_symbols = []
  stock_interval = None

  # parse parameters
  if symbol:
    stock_symbols = list(symbol)
  else:
    click.echo('讀取設定檔: {}'.format(config.name))
    stock_symbols = [line.strip() for line in config if line.strip()]
  if interval:
    stock_interval = 60 if interval < 60 else interval

  # create object
  twse_lib = TWSELIB()
  for stock_symbol in stock_symbols:
    key = twse_lib.get_stock_key(stock_symbol)
    stock_keys.append(key)
  while True:
    stock_infos = twse_lib.get_stock_info(stock_keys)
    if stock_infos:
      if stock_interval:
        os.system('clear')
      print2terminal(stock_infos)
      if stock_interval:
        try:
          print('資料更新頻率: {}s'.format(stock_interval))
          time.sleep(stock_interval)
        except KeyboardInterrupt:
          break
      else:
        break
    else:
      break

  # delete object
  del twse_lib
  pass


if __name__ == '__main__':
  cli()
