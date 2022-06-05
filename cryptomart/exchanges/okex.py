import datetime
import os
from typing import List

import pandas as pd
from cryptomart.interfaces.instrument_info import InstrumentInfoInterface
from cryptomart.interfaces.order_book import OrderBookInterface
from requests import Request

from ..enums import Instrument, InstrumentType, Interface, Interval, OrderBookSchema
from ..feeds import OHLCVColumn
from ..interfaces.ohlcv import OHLCVInterface
from ..types import IntervalType
from ..util import Dispatcher, dt_to_timestamp
from .base import ExchangeAPIBase


def instrument_info_perp(dispatcher: Dispatcher, url: str) -> pd.DataFrame:
    col_map = {
        "ctValCcy": Instrument.cryptomart_symbol,
        "instId": Instrument.exchange_symbol,
        "ctVal": Instrument.orderbook_multi,
        "listTime": Instrument.exchange_list_time,
    }
    params = {
        "instType": "SWAP",
    }
    request = Request("GET", url, params=params)
    response = dispatcher.send_request(request)

    df = InstrumentInfoInterface.handle_response(response, ["data"], ["code"], "0", ["msg"], col_map)
    df = df[df.state == "live"]
    df = df[df.ctType == "linear"]
    df = df[df.settleCcy == "USDT"]
    return df


def instrument_info_spot(dispatcher: Dispatcher, url: str) -> pd.DataFrame:
    col_map = {
        "baseCcy": Instrument.cryptomart_symbol,
        "instId": Instrument.exchange_symbol,
        "listTime": Instrument.exchange_list_time,
    }
    params = {
        "instType": "SPOT",
    }
    request = Request("GET", url, params=params)
    response = dispatcher.send_request(request)

    df = InstrumentInfoInterface.handle_response(response, ["data"], ["code"], "0", ["msg"], col_map)
    df = df[df.state == "live"]
    df = df[df.quoteCcy == "USDT"]
    return df


def ohlcv(
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
        6: OHLCVColumn.volume,
    }
    reqs = []
    for starttime, endtime, limit in zip(starttimes, endtimes, limits):
        req = Request(
            "GET",
            url,
            params={
                "instId": instrument_id,
                "bar": interval_id,
                "before": dt_to_timestamp(starttime, granularity="milliseconds"),
                "after": dt_to_timestamp(endtime, granularity="milliseconds"),
                "limit": limit,
            },
        )
        reqs.append(req)

    responses = dispatcher.send_requests(reqs)
    return OHLCVInterface.format_responses(responses, ["data"], ["code"], "0", ["msg"], col_map)


def order_book(dispatcher: Dispatcher, url: str, instrument_id: str, depth: int = 20) -> pd.DataFrame:
    col_map = {
        0: OrderBookSchema.price,
        1: OrderBookSchema.quantity,
    }
    request = Request(
        "GET",
        url,
        params={
            "instId": instrument_id,
            "sz": depth,
        },
    )

    response = dispatcher.send_request(request)
    orderbook = OrderBookInterface.handle_response(
        response, ["data", 0], ["code"], "0", ["msg"], col_map, ("bids", "asks")
    )
    return orderbook


class OKEx(ExchangeAPIBase):

    name = "okex"
    base_url = "https://www.okx.com"

    intervals = {
        Interval.interval_1h: ("1m", datetime.timedelta(hours=1)),
        Interval.interval_5m: ("5m", datetime.timedelta(hours=1)),
        Interval.interval_15m: ("15m", datetime.timedelta(hours=1)),
        Interval.interval_1h: ("1H", datetime.timedelta(hours=1)),
        Interval.interval_4h: ("4H", datetime.timedelta(hours=4)),
        Interval.interval_12h: ("12Hutc", datetime.timedelta(hours=12)),
        Interval.interval_1d: ("1Dutc", datetime.timedelta(days=1)),
    }

    def __init__(self, cache_kwargs={"disabled": False, "refresh": False}, log_level: str = "DEBUG"):
        super().__init__(cache_kwargs=cache_kwargs, log_level=log_level)
        self.init_dispatchers()
        self.init_instrument_info_interface()
        self.init_ohlcv_interface()
        self.init_order_book_interface()

    def init_dispatchers(self):
        self.logger.debug("initializing dispatchers")
        self.dispatcher = Dispatcher(f"{self.name}.dispatcher.perpetual", timeout=1 / 5)

    def init_instrument_info_interface(self):
        perpetual = InstrumentInfoInterface(
            exchange=self,
            interface_name=Interface.INSTRUMENT_INFO,
            inst_type=InstrumentType.PERPETUAL,
            url=os.path.join(self.base_url, "api/v5/public/instruments"),
            dispatcher=self.dispatcher,
            execute=instrument_info_perp,
        )

        spot = InstrumentInfoInterface(
            exchange=self,
            interface_name=Interface.INSTRUMENT_INFO,
            inst_type=InstrumentType.SPOT,
            url=os.path.join(self.base_url, "api/v5/public/instruments"),
            dispatcher=self.dispatcher,
            execute=instrument_info_spot,
        )

        self.interfaces[Interface.INSTRUMENT_INFO] = {
            InstrumentType.PERPETUAL: perpetual,
            InstrumentType.SPOT: spot,
        }

    def init_ohlcv_interface(self):
        perpetual = OHLCVInterface(
            intervals=self.intervals,
            start_inclusive=False,
            end_inclusive=True,
            max_response_limit=100,
            exchange=self,
            interface_name=Interface.OHLCV,
            inst_type=InstrumentType.PERPETUAL,
            url=os.path.join(self.base_url, "api/v5/market/history-candles"),
            dispatcher=self.dispatcher,
            execute=ohlcv,
        )

        spot = OHLCVInterface(
            intervals=self.intervals,
            start_inclusive=False,
            end_inclusive=True,
            max_response_limit=100,
            exchange=self,
            interface_name=Interface.OHLCV,
            inst_type=InstrumentType.SPOT,
            url=os.path.join(self.base_url, "api/v5/market/history-candles"),
            dispatcher=self.dispatcher,
            execute=ohlcv,
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
            url=os.path.join(self.base_url, "api/v5/market/books"),
            dispatcher=self.dispatcher,
            execute=order_book,
        )

        spot = OrderBookInterface(
            exchange=self,
            interface_name=Interface.ORDER_BOOK,
            inst_type=InstrumentType.SPOT,
            url=os.path.join(self.base_url, "api/v5/market/books"),
            dispatcher=self.dispatcher,
            execute=order_book,
        )

        self.interfaces[Interface.ORDER_BOOK] = {
            InstrumentType.PERPETUAL: perpetual,
            InstrumentType.SPOT: spot,
        }


_exchange_export = OKEx
