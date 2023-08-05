[![Travis Build Status](https://travis-ci.org/hansliu/twsecli.svg?branch=master)](https://travis-ci.org/hansliu/twsecli) [![PyPI version](https://badge.fury.io/py/twsecli.svg)](https://badge.fury.io/py/twsecli) [![GitHub license](https://img.shields.io/github/license/hansliu/twsecli.svg)](https://github.com/hansliu/twsecli/blob/master/LICENSE)

# twsecli
TWSE unofficial command line interface

提供 Cli 介面，根據台灣股票代號，顯示台灣證券交易所即時股價。

![Imgur](https://i.imgur.com/RqWAhpm.png)

## Install / 安裝

```
pip3 install twsecli
```

## Usage / 執行

```
twsecli <stock symbol>
twsecli -n 300 <stock symbol>
twsecli -n 300 -c .twsecli_config
twsecli -h
```
