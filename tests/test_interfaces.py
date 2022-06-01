import importlib
import logging
from datetime import datetime

import pytest
from cryptomart.client import Client
from cryptomart.enums import (Exchange, InstrumentType, Interval,
                              OrderBookSchema, OrderBookSide, Symbol)
from cryptomart.exchanges import Binance
from cryptomart.exchanges.base import ExchangeAPIBase, NotSupportedError

DONT_TEST = {
    Exchange.BYBIT,
    Exchange.BITMEX,
    Exchange.COINFLEX,
    Exchange.FTX,
    Exchange.GATEIO,
    Exchange.KUCOIN,
    Exchange.OKEX,
}

@pytest.fixture(params=set(Exchange._values()) - DONT_TEST)
def exchange(request):
    exchange_id = request.param
    exchange_module = importlib.import_module(f"cryptomart.exchanges.{exchange_id}")
    exchange_class = exchange_module._exchange_export
    exchange_instance = exchange_class()

def test_ohlcv_interface(exchange)
