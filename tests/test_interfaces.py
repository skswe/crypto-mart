import importlib
import logging
from datetime import datetime

import pytest
from cryptomart.enums import Exchange, InstrumentType, Interval, Symbol
from cryptomart.errors import NotSupportedError
from cryptomart.exchanges.base import ExchangeAPIBase

DONT_TEST = {
    Exchange.BYBIT,
    Exchange.BITMEX,
    Exchange.COINFLEX,
    Exchange.FTX,
    Exchange.GATEIO,
    Exchange.KUCOIN,
    Exchange.OKEX,
}

logging.getLogger("cryptomart.binance").setLevel("DEBUG")


@pytest.fixture(params=set(Exchange._values()) - DONT_TEST)
def exchange(request) -> ExchangeAPIBase:
    exchange_id = request.param
    exchange_module = importlib.import_module(f"cryptomart.exchanges.{exchange_id}")
    exchange_class = exchange_module._exchange_export
    exchange_instance = exchange_class()
    return exchange_instance


@pytest.mark.requires_http
def test_init(exchange: ExchangeAPIBase):
    pass


@pytest.mark.requires_http
def test_instrument_info(exchange: ExchangeAPIBase):
    exchange.instrument_info(InstrumentType.PERPETUAL)
    exchange.instrument_info(InstrumentType.SPOT)


@pytest.mark.parametrize("inst_type", [InstrumentType.PERPETUAL, InstrumentType.SPOT])
@pytest.mark.parametrize("symbol", [Symbol.BTC, Symbol.ETH, Symbol.ADA, Symbol.DOGE])
@pytest.mark.parametrize("interval", [Interval.interval_1d])
@pytest.mark.parametrize(["starttime", "endtime"], [(datetime(2021, 10, 1), datetime(2021, 12, 3))])
@pytest.mark.requires_http
def test_ohlcv(
    exchange: ExchangeAPIBase,
    symbol: Symbol,
    inst_type: InstrumentType,
    interval: Interval,
    starttime: datetime,
    endtime: datetime,
):
    try:
        exchange.ohlcv(symbol, inst_type, interval, starttime, endtime, disable_cache=True)
    except NotSupportedError as e:
        pytest.skip(str(e))
