import logging
from datetime import datetime

import pytest
from cryptomart.client import Client
from cryptomart.enums import Exchange, Instrument, InstrumentType, Interval, OrderBookSchema, OrderBookSide
from cryptomart.exchanges.base import ExchangeAPIBase, NotSupportedError

PRINT = False
LOG_LEVEL = "DEBUG"
CACHE_KWARGS = {"disabled": True}
WHITELIST = set(Exchange._values())
# BLACKLIST = set(Exchange._values())
# WHITELIST = set({Exchange.KUCOIN})
BLACKLIST = set({})
EXCHANGES = WHITELIST - BLACKLIST


@pytest.fixture(scope="module")
def client():
    return Client(cache_kwargs=CACHE_KWARGS, log_level=LOG_LEVEL)


@pytest.fixture(params=EXCHANGES)
def exchange(client, request):
    return getattr(client, request.param)


@pytest.mark.parametrize("inst_type", [InstrumentType.PERPETUAL, InstrumentType.SPOT])
@pytest.mark.requires_http
def test_instrument_info(exchange: ExchangeAPIBase, inst_type: InstrumentType):
    df = exchange.instrument_info(inst_type)
    assert not df.empty
    assert set(Instrument._values()).issubset(set(df.columns))
    if PRINT:
        print(df)


@pytest.mark.parametrize("inst_type", [InstrumentType.SPOT, InstrumentType.PERPETUAL])
@pytest.mark.parametrize("symbol", ["BTC", "ADA", "DOGE"])
@pytest.mark.parametrize("interval", [Interval.interval_1d, Interval.interval_1h])
@pytest.mark.parametrize(["starttime", "endtime"], [(datetime(2022, 5, 25), datetime(2022, 6, 3))])
@pytest.mark.requires_http
def test_ohlcv(
    exchange: ExchangeAPIBase,
    symbol: str,
    inst_type: InstrumentType,
    interval: Interval,
    starttime: datetime,
    endtime: datetime,
):
    try:
        df = exchange.ohlcv(symbol, inst_type, starttime, endtime, interval)
        timedelta = exchange._get_interface("ohlcv", inst_type).intervals[interval][1]
        assert df.open_time.iloc[0] == starttime
        assert df.open_time.iloc[-1] == endtime - timedelta
        assert (len(df.dropna()) / len(df)) > 0.4, "Missing data"
        if PRINT:
            print(df.gaps)
    except NotSupportedError as e:
        pytest.skip(str(e))


@pytest.mark.parametrize("inst_type", [InstrumentType.PERPETUAL, InstrumentType.SPOT])
@pytest.mark.parametrize("symbol", ["BTC", "ETH"])
@pytest.mark.parametrize("depth", [20])
@pytest.mark.requires_http
def test_orderbook(exchange: ExchangeAPIBase, symbol: str, inst_type: InstrumentType, depth: int):
    orderbook = exchange.order_book(symbol, inst_type, depth)
    assert sorted(orderbook.columns) == sorted(OrderBookSchema._names())

    bids = orderbook[orderbook[OrderBookSchema.side] == OrderBookSide.bid].reset_index(drop=True)
    asks = orderbook[orderbook[OrderBookSchema.side] == OrderBookSide.ask].reset_index(drop=True)

    correct_bids = bids.sort_values(OrderBookSchema.price, ascending=False, ignore_index=True)
    correct_asks = asks.sort_values(OrderBookSchema.price, ascending=True, ignore_index=True)

    assert (bids == correct_bids).all(axis=None)
    assert (asks == correct_asks).all(axis=None)

    if PRINT:
        print(orderbook)


@pytest.mark.parametrize("symbol", ["BTC", "ADA", "DOGE"])
@pytest.mark.parametrize(["starttime", "endtime"], [(datetime(2022, 5, 25), datetime(2022, 6, 3))])
@pytest.mark.requires_http
def test_funding_rate(exchange: ExchangeAPIBase, symbol: str, starttime: datetime, endtime: datetime):
    try:
        df = exchange.funding_rate(symbol, starttime, endtime)
        timedelta = exchange._get_interface("funding_rate", "perpetual").funding_interval
        assert df.timestamp.iloc[0] == starttime
        assert df.timestamp.iloc[-1] == endtime - timedelta
        assert (len(df.dropna()) / len(df)) >= 0.0, "Missing data"
    except NotSupportedError as e:
        pytest.skip(str(e))
