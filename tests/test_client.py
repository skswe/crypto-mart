import logging
from datetime import datetime

import pytest
from cryptomart.client import Client
from cryptomart.enums import Exchange, InstrumentType, Interval, OrderBookSchema, OrderBookSide, Symbol
from cryptomart.exchanges.base import ExchangeAPIBase, NotSupportedError

logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def client():
    return Client()


@pytest.fixture(params=Exchange._values())
def exchange(client, request):
    return getattr(client, request.param)


@pytest.mark.parametrize("instType", [InstrumentType.PERPETUAL, InstrumentType.QUARTERLY])
@pytest.mark.parametrize("symbol", [Symbol.BTC, Symbol.ETH, Symbol.ADA, Symbol.DOGE])
@pytest.mark.parametrize("interval", [Interval.interval_1d])
@pytest.mark.parametrize(["starttime", "endtime"], [(datetime(2021, 10, 1), datetime(2021, 12, 3))])
@pytest.mark.requires_http
def test_ohlcv(exchange: ExchangeAPIBase, instType, symbol, interval, starttime, endtime):
    try:
        exchange.ohlcv(instType, symbol, interval, starttime, endtime, disable_cache=True)
    except NotSupportedError as e:
        pytest.skip(str(e))


@pytest.mark.parametrize("instType", [InstrumentType.PERPETUAL])
@pytest.mark.parametrize("symbol", [Symbol.BTC, Symbol.ETH])
@pytest.mark.parametrize("depth", [20])
@pytest.mark.requires_http
def test_orderbook(exchange: ExchangeAPIBase, instType, symbol, depth):
    orderbook = exchange.order_book(symbol, instType, depth)
    assert (orderbook.columns == OrderBookSchema._names()).all()

    bids = orderbook[orderbook[OrderBookSchema.side] == OrderBookSide.bid].reset_index(drop=True)
    asks = orderbook[orderbook[OrderBookSchema.side] == OrderBookSide.ask].reset_index(drop=True)

    correct_bids = bids.sort_values(OrderBookSchema.price, ascending=False, ignore_index=True)
    correct_asks = asks.sort_values(OrderBookSchema.price, ascending=True, ignore_index=True)

    assert (bids == correct_bids).all(axis=None)
    assert (asks == correct_asks).all(axis=None)
