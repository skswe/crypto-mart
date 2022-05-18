import logging
from datetime import datetime, timedelta

import pytest
from cryptomart.client import Client
from cryptomart.enums import Exchange, Instrument, InstrumentType, Interval, OrderBookSchema, OrderBookSide, Symbol
from cryptomart.exchanges.base import ExchangeAPIBase, NotSupportedError

logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def client():
    return Client()


# @pytest.fixture(params=[Exchange.KUCOIN])
@pytest.fixture(params=list(set(Exchange._values()) - {Exchange.BYBIT, Exchange.KUCOIN}))
def exchange(client, request):
    return getattr(client, request.param)


@pytest.mark.parametrize("symbol", [Symbol.BTC, Symbol.ETH, Symbol.ADA, Symbol.DOGE])
@pytest.mark.parametrize("instType", [InstrumentType.PERPETUAL, InstrumentType.QUARTERLY])
@pytest.mark.parametrize("interval", [Interval.interval_1d])
@pytest.mark.parametrize(["starttime", "endtime"], [(datetime(2022, 3, 12), datetime(2022, 5, 13))])
@pytest.mark.requires_http
def test_ohlcv(exchange: ExchangeAPIBase, symbol, instType, interval, starttime, endtime):
    try:
        exchange.ohlcv(symbol, instType, interval, starttime, endtime, disable_cache=True)
    except NotSupportedError as e:
        pytest.skip(str(e))


@pytest.mark.parametrize("symbol", [Symbol.BTC, Symbol.ETH])
@pytest.mark.parametrize("instType", [InstrumentType.PERPETUAL])
@pytest.mark.parametrize("depth", [20])
@pytest.mark.requires_http
def test_orderbook(exchange: ExchangeAPIBase, symbol, instType, depth):
    orderbook = exchange.order_book(symbol, instType, depth)
    assert (orderbook.columns == OrderBookSchema._names()).all()

    bids = orderbook[orderbook[OrderBookSchema.side] == OrderBookSide.bid].reset_index(drop=True)
    asks = orderbook[orderbook[OrderBookSchema.side] == OrderBookSide.ask].reset_index(drop=True)

    correct_bids = bids.sort_values(OrderBookSchema.price, ascending=False, ignore_index=True)
    correct_asks = asks.sort_values(OrderBookSchema.price, ascending=True, ignore_index=True)

    assert (bids == correct_bids).all(axis=None)
    assert (asks == correct_asks).all(axis=None)


@pytest.mark.parametrize("symbol", [Symbol.BTC])
@pytest.mark.parametrize("instType", [InstrumentType.PERPETUAL])
@pytest.mark.parametrize(["starttime", "endtime"], [(datetime(2022, 4, 15), datetime(2022, 5, 19))])
@pytest.mark.parametrize("timedelta", [timedelta(days=1)])
@pytest.mark.requires_http
def test_funding_rate(exchange: ExchangeAPIBase, symbol, instType, starttime, endtime, timedelta):
    symbol_name = exchange.get_instrument(symbol, instType)[Instrument.contract_name]

    funding_rate = exchange._funding_rate(
        symbol_name, instType, starttime, endtime, timedelta, cache_kwargs={"disabled": True}
    )

    # print(funding_rate)

    assert funding_rate.iloc[0].timestamp == starttime
    assert funding_rate.iloc[-1].timestamp == endtime - timedelta
    missing_pct = funding_rate.funding_rate.isna().sum() / len(funding_rate)
    assert missing_pct < 0.5
