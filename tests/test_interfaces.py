import importlib
import logging
from datetime import datetime, timedelta

import numpy as np
import pytest
from cryptomart.enums import Exchange, Instrument, InstrumentType, Interval, OrderBookSchema, OrderBookSide, Symbol
from cryptomart.errors import NotSupportedError
from cryptomart.exchanges.base import ExchangeAPIBase
from cryptomart.util import parse_time

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


@pytest.fixture(params=set(Exchange._values()) - DONT_TEST, scope="module")
def exchange(request) -> ExchangeAPIBase:
    exchange_id = request.param
    exchange_module = importlib.import_module(f"cryptomart.exchanges.{exchange_id}")
    exchange_class = exchange_module._exchange_export
    exchange_instance = exchange_class(cache_kwargs={"disabled": True})
    return exchange_instance


@pytest.mark.requires_http
def test_init(exchange: ExchangeAPIBase):
    pass


@pytest.mark.parametrize("inst_type", [InstrumentType.PERPETUAL, InstrumentType.SPOT])
@pytest.mark.requires_http
def test_instrument_info(exchange: ExchangeAPIBase, inst_type: InstrumentType):
    df = exchange.instrument_info(inst_type)
    assert not df.empty


@pytest.mark.parametrize("inst_type", [InstrumentType.PERPETUAL, InstrumentType.SPOT])
@pytest.mark.parametrize("symbol", [Symbol.BTC, Symbol.ADA, Symbol.DOGE])
@pytest.mark.parametrize("interval", [Interval.interval_1d, Interval.interval_1h])
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
        df = exchange.ohlcv(symbol, inst_type, interval, starttime, endtime)
        timedelta = exchange._get_interface("ohlcv", inst_type).intervals[interval][1]
        assert df.open_time.iloc[0] == starttime
        assert df.open_time.iloc[-1] == endtime - timedelta
    except NotSupportedError as e:
        pytest.skip(str(e))


@pytest.mark.parametrize("inst_type", [InstrumentType.PERPETUAL, InstrumentType.SPOT])
@pytest.mark.parametrize("symbol", [Symbol.BTC, Symbol.ETH])
@pytest.mark.parametrize("depth", [20])
@pytest.mark.requires_http
def test_orderbook(exchange: ExchangeAPIBase, symbol: Symbol, inst_type: InstrumentType, depth: int):
    orderbook = exchange.order_book(symbol, inst_type, depth)
    assert (orderbook.columns == OrderBookSchema._names()).all()

    bids = orderbook[orderbook[OrderBookSchema.side] == OrderBookSide.bid].reset_index(drop=True)
    asks = orderbook[orderbook[OrderBookSchema.side] == OrderBookSide.ask].reset_index(drop=True)

    correct_bids = bids.sort_values(OrderBookSchema.price, ascending=False, ignore_index=True)
    correct_asks = asks.sort_values(OrderBookSchema.price, ascending=True, ignore_index=True)

    assert (bids == correct_bids).all(axis=None)
    assert (asks == correct_asks).all(axis=None)


@pytest.mark.parametrize("inst_type", [InstrumentType.PERPETUAL, InstrumentType.SPOT])
@pytest.mark.requires_http
def test_listing_dates_accurate(exchange: ExchangeAPIBase, inst_type: InstrumentType):
    listing_dates = exchange.instrument_info(inst_type)[[Instrument.cryptomart_symbol, Instrument.listing_date]]
    for idx, row in listing_dates.iterrows():
        if row.listing_date == np.nan:
            exchange.logger.warning(f"nan listing for {row.cryptomart_symbol}")
            continue
        try:
            df = exchange.ohlcv(
                row.cryptomart_symbol,
                inst_type,
                Interval.interval_1d,
                parse_time(row.listing_date),
                parse_time(row.listing_date) + timedelta(days=7),
            )
            exchange.logger.warning(
                f"listing_date was {row.listing_date} but first open_time was {df.iloc[0].open_time}"
            )
        except NotSupportedError:
            continue
