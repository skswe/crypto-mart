import datetime
import os
from typing import List

import pandas as pd
from requests import Request

from ..enums import Instrument, InstrumentType, Interface, Interval, OrderBookSchema, OrderBookSide
from ..feeds import OHLCVColumn
from ..interfaces.funding_rate import FundingRateInterface
from ..interfaces.instrument_info import InstrumentInfoInterface
from ..interfaces.ohlcv import OHLCVInterface
from ..interfaces.order_book import OrderBookInterface
from ..types import IntervalType
from ..util import Dispatcher, dt_to_timestamp
from .base import ExchangeAPIBase


def instrument_info_perp(dispatcher: Dispatcher, url: str) -> pd.DataFrame:
    col_map = {
        "base_currency": Instrument.cryptomart_symbol,
        "name": Instrument.exchange_symbol,
    }
    request = Request("GET", url)
    response = dispatcher.send_request(request)
    df = InstrumentInfoInterface.handle_response(response, ["result"], ["ret_code"], 0, ["ret_msg"], col_map)
    df = df[df.status == "Trading"]

    # filter out symbols that end in a number
    df = df[df.name.apply(lambda e: e[-1] not in [str(x) for x in range(0, 9)])]
    df = df[df.quote_currency == "USDT"]
    return df


def instrument_info_spot(dispatcher: Dispatcher, url: str) -> pd.DataFrame:
    col_map = {
        "baseCurrency": Instrument.cryptomart_symbol,
        "name": Instrument.exchange_symbol,
    }
    request = Request("GET", url)
    response = dispatcher.send_request(request)
    df = InstrumentInfoInterface.handle_response(response, ["result"], ["ret_code"], 0, ["ret_msg"], col_map)

    # filter out symbols that end in a number
    df = df[df.name.apply(lambda e: e[-1] not in [str(x) for x in range(0, 9)])]
    df = df[df.quoteCurrency == "USDT"]
    return df


def ohlcv_perp(
    dispatcher: Dispatcher,
    url: str,
    instrument_id: str,
    interval_id: IntervalType,
    starttimes: List[datetime.datetime],
    endtimes: List[datetime.datetime],
    limits: List[int],
) -> pd.DataFrame:
    col_map = {
        "open_time": OHLCVColumn.open_time,
        "open": OHLCVColumn.open,
        "high": OHLCVColumn.high,
        "low": OHLCVColumn.low,
        "close": OHLCVColumn.close,
        "volume": OHLCVColumn.volume,
    }
    reqs = []
    for starttime, endtime, limit in zip(starttimes, endtimes, limits):
        req = Request(
            "GET",
            url,
            params={
                "symbol": instrument_id,
                "interval": interval_id,
                "from": dt_to_timestamp(starttime, granularity="seconds"),
                "limit": limit,
            },
        )
        reqs.append(req)

    responses = dispatcher.send_requests(reqs)
    return OHLCVInterface.format_responses(responses, ["result"], ["ret_code"], 0, ["ret_msg"], col_map)


def ohlcv_spot(
    dispatcher: Dispatcher,
    url: str,
    instrument_id: str,
    interval_id: IntervalType,
    starttimes: List[datetime.datetime],
    endtimes: List[datetime.datetime],
    limits: List[int],
) -> pd.DataFrame:
    col_map = {
        0: OHLCVColumn.open_time,
        1: OHLCVColumn.open,
        2: OHLCVColumn.high,
        3: OHLCVColumn.low,
        4: OHLCVColumn.close,
        5: OHLCVColumn.volume,
    }
    reqs = []
    for starttime, endtime, limit in zip(starttimes, endtimes, limits):
        req = Request(
            "GET",
            url,
            params={
                "symbol": instrument_id,
                "interval": interval_id,
                "startTime": dt_to_timestamp(starttime, granularity="milliseconds"),
                "endTime": dt_to_timestamp(endtime, granularity="milliseconds"),
                "limit": limit,
            },
        )
        reqs.append(req)

    responses = dispatcher.send_requests(reqs)
    return OHLCVInterface.format_responses(responses, ["result"], ["ret_code"], 0, ["ret_msg"], col_map)


def funding_rate(
    dispatcher: Dispatcher,
    url: str,
    instrument_id: str,
    starttimes: List[datetime.datetime],
    endtimes: List[datetime.datetime],
    limits: List[int],
):
    col_map = {}
    reqs = []
    for starttime, endtime, limit in zip(starttimes, endtimes, limits):
        req = Request(
            "GET",
            url,
            params={},
        )
        reqs.append(req)

    responses = dispatcher.send_requests(reqs)
    return FundingRateInterface.format_responses(responses, [], [], None, [], col_map)


def order_book_perp(dispatcher: Dispatcher, url: str, instrument_name: str, depth: int = 20) -> pd.DataFrame:
    col_map = {
        "price": OrderBookSchema.price,
        "size": OrderBookSchema.quantity,
        "side": OrderBookSchema.side,
    }
    request = Request(
        "GET",
        url,
        params={
            "symbol": instrument_name,
        },
    )
    response = dispatcher.send_request(request)
    orderbook = OrderBookInterface.handle_response(response, ["result"], ["ret_code"], 0, ["ret_msg"], col_map, ())
    orderbook.replace("Sell", OrderBookSide.ask, inplace=True)
    orderbook.replace("Buy", OrderBookSide.bid, inplace=True)
    return orderbook


def order_book_spot(dispatcher: Dispatcher, url: str, instrument_id: str, depth: int = 20) -> pd.DataFrame:
    col_map = {
        0: OrderBookSchema.price,
        1: OrderBookSchema.quantity,
    }
    request = Request(
        "GET",
        url,
        params={
            "symbol": instrument_id,
        },
    )
    response = dispatcher.send_request(request)
    orderbook = OrderBookInterface.handle_response(
        response, ["result"], ["ret_code"], 0, ["ret_msg"], col_map, ("bids", "asks")
    )
    return orderbook


class Bybit(ExchangeAPIBase):

    name = "bybit"
    base_url = "https://api.bybit.com"

    intervals_perp = {
        Interval.interval_1m: (1, datetime.timedelta(minutes=1)),
        Interval.interval_5m: (5, datetime.timedelta(minutes=5)),
        Interval.interval_15m: (15, datetime.timedelta(minutes=15)),
        Interval.interval_1h: (60, datetime.timedelta(hours=1)),
        Interval.interval_4h: (240, datetime.timedelta(hours=4)),
        Interval.interval_12h: (720, datetime.timedelta(hours=12)),
        Interval.interval_1d: ("D", datetime.timedelta(days=1)),
    }

    intervals_spot = {
        Interval.interval_1m: ("1m", datetime.timedelta(minutes=1)),
        Interval.interval_5m: ("5m", datetime.timedelta(minutes=5)),
        Interval.interval_15m: ("15m", datetime.timedelta(minutes=15)),
        Interval.interval_1h: ("1h", datetime.timedelta(hours=1)),
        Interval.interval_4h: ("4h", datetime.timedelta(hours=4)),
        Interval.interval_12h: ("12h", datetime.timedelta(hours=12)),
        Interval.interval_1d: ("1d", datetime.timedelta(days=1)),
    }

    def __init__(self, cache_kwargs={"disabled": False, "refresh": False}, log_level: str = "INFO"):
        super().__init__(cache_kwargs=cache_kwargs, log_level=log_level)
        self.init_dispatchers()
        self.init_instrument_info_interface()
        self.init_ohlcv_interface()
        self.init_order_book_interface()

    def init_dispatchers(self):
        # Check which endpoints employ a limit
        self.logger.debug("initializing dispatchers")
        self.dispatcher = Dispatcher(f"{self.name}.dispatcher", timeout=1 / 40)

    def init_instrument_info_interface(self):
        perpetual = InstrumentInfoInterface(
            exchange=self,
            interface_name=Interface.INSTRUMENT_INFO,
            inst_type=InstrumentType.PERPETUAL,
            url=os.path.join(self.base_url, "v2/public/symbols"),
            dispatcher=self.dispatcher,
            execute=instrument_info_perp,
        )

        spot = InstrumentInfoInterface(
            exchange=self,
            interface_name=Interface.INSTRUMENT_INFO,
            inst_type=InstrumentType.SPOT,
            url=os.path.join(self.base_url, "spot/v1/symbols"),
            dispatcher=self.dispatcher,
            execute=instrument_info_spot,
        )

        self.interfaces[Interface.INSTRUMENT_INFO] = {
            InstrumentType.PERPETUAL: perpetual,
            InstrumentType.SPOT: spot,
        }

    def init_ohlcv_interface(self):
        perpetual = OHLCVInterface(
            intervals=self.intervals_perp,
            start_inclusive=True,
            end_inclusive=False,
            max_response_limit=200,
            exchange=self,
            interface_name=Interface.OHLCV,
            inst_type=InstrumentType.PERPETUAL,
            url=os.path.join(self.base_url, "public/linear/kline"),
            dispatcher=self.dispatcher,
            execute=ohlcv_perp,
        )

        spot = OHLCVInterface(
            intervals=self.intervals_spot,
            start_inclusive=False,
            end_inclusive=False,
            max_response_limit=1000,
            exchange=self,
            interface_name=Interface.OHLCV,
            inst_type=InstrumentType.SPOT,
            url=os.path.join(self.base_url, "spot/quote/v1/kline"),
            dispatcher=self.dispatcher,
            execute=ohlcv_spot,
        )

        self.interfaces[Interface.OHLCV] = {
            InstrumentType.PERPETUAL: perpetual,
            InstrumentType.SPOT: spot,
        }

    def init_order_book_interface(self):
        perpetual = OrderBookInterface(
            exchange=self,
            interface_name=Interface.ORDER_BOOK,
            inst_type=InstrumentType.PERPETUAL,
            url=os.path.join(self.base_url, "v2/public/orderBook/L2"),
            dispatcher=self.dispatcher,
            execute=order_book_perp,
        )

        spot = OrderBookInterface(
            exchange=self,
            interface_name=Interface.ORDER_BOOK,
            inst_type=InstrumentType.SPOT,
            url=os.path.join(self.base_url, "spot/quote/v1/depth"),
            dispatcher=self.dispatcher,
            execute=order_book_spot,
        )

        self.interfaces[Interface.ORDER_BOOK] = {
            InstrumentType.PERPETUAL: perpetual,
            InstrumentType.SPOT: spot,
        }


_exchange_export = Bybit
