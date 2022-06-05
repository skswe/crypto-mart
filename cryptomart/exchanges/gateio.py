import datetime
import os
from typing import List

import pandas as pd
from cryptomart.interfaces.instrument_info import InstrumentInfoInterface
from cryptomart.interfaces.order_book import OrderBookInterface
from requests import Request

from ..enums import Instrument, InstrumentType, Interface, Interval, OrderBookSchema, OrderBookSide
from ..feeds import OHLCVColumn
from ..interfaces.ohlcv import OHLCVInterface
from ..types import IntervalType
from ..util import Dispatcher, dt_to_timestamp
from .base import ExchangeAPIBase


def instrument_info_perp(dispatcher: Dispatcher, url: str) -> pd.DataFrame:
    col_map = {
        "name": Instrument.exchange_symbol,
        "quanto_multiplier": Instrument.orderbook_multi,
    }
    request = Request("GET", url)
    response = dispatcher.send_request(request)
    df = InstrumentInfoInterface.handle_response(response, [], [], None, ["message"], col_map)
    df[Instrument.cryptomart_symbol] = df.name.apply(lambda e: e.replace("_USDT", ""))

    df = df[df.in_delisting == False]
    df = df[df.type == "direct"]
    return df


def instrument_info_spot(dispatcher: Dispatcher, url: str) -> pd.DataFrame:
    col_map = {
        "base": Instrument.cryptomart_symbol,
        "id": Instrument.exchange_symbol,
    }
    request = Request("GET", url)
    response = dispatcher.send_request(request)
    df = InstrumentInfoInterface.handle_response(response, [], [], None, ["message"], col_map)

    df = df[df.trade_status == "tradable"]
    df = df[df.quote == "USDT"]
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
        "t": OHLCVColumn.open_time,
        "o": OHLCVColumn.open,
        "h": OHLCVColumn.high,
        "l": OHLCVColumn.low,
        "c": OHLCVColumn.close,
        "v": OHLCVColumn.volume,
    }
    reqs = []
    for starttime, endtime, limit in zip(starttimes, endtimes, limits):
        req = Request(
            "GET",
            url,
            params={
                "contract": instrument_id,
                "interval": interval_id,
                "from": dt_to_timestamp(starttime, granularity="seconds"),
                "to": dt_to_timestamp(endtime, granularity="seconds"),
            },
        )
        reqs.append(req)

    responses = dispatcher.send_requests(reqs)
    return OHLCVInterface.format_responses(responses, [], [], None, ["message"], col_map)


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
        5: OHLCVColumn.open,
        3: OHLCVColumn.high,
        4: OHLCVColumn.low,
        2: OHLCVColumn.close,
        1: OHLCVColumn.volume,
    }
    reqs = []
    for starttime, endtime, limit in zip(starttimes, endtimes, limits):
        req = Request(
            "GET",
            url,
            params={
                "currency_pair": instrument_id,
                "interval": interval_id,
                "from": dt_to_timestamp(starttime, granularity="seconds"),
                "to": dt_to_timestamp(endtime, granularity="seconds"),
            },
        )
        reqs.append(req)

    responses = dispatcher.send_requests(reqs)
    return OHLCVInterface.format_responses(responses, [], [], None, ["message"], col_map)


def order_book_perp(dispatcher: Dispatcher, url: str, instrument_name: str, depth: int = 20) -> pd.DataFrame:
    col_map = {
        "p": OrderBookSchema.price,
        "s": OrderBookSchema.quantity,
    }
    request = Request(
        "GET",
        url,
        params={
            "contract": instrument_name,
            "limit": depth,
        },
    )
    response = dispatcher.send_request(request)
    orderbook = OrderBookInterface.handle_response(response, [], [], None, ["message"], col_map, ("bids", "asks"))
    return orderbook


def order_book_spot(dispatcher: Dispatcher, url: str, instrument_id: str, depth: int = 20) -> pd.DataFrame:
    col_map = {
        0: OrderBookSchema.price,
        1: OrderBookSchema.quantity,
    }
    request = Request(
        "GET",
        url,
        params={"currency_pair": instrument_id, "limit": depth},
    )
    response = dispatcher.send_request(request)
    orderbook = OrderBookInterface.handle_response(response, [], [], None, ["message"], col_map, ("bids", "asks"))
    return orderbook


class GateIO(ExchangeAPIBase):

    name = "gateio"
    base_url = "https://api.gateio.ws/api/v4"

    intervals = {
        Interval.interval_1m: ("1m", datetime.timedelta(minutes=1)),
        Interval.interval_5m: ("5m", datetime.timedelta(minutes=5)),
        Interval.interval_15m: ("15m", datetime.timedelta(minutes=15)),
        Interval.interval_1h: ("1h", datetime.timedelta(hours=1)),
        Interval.interval_4h: ("4h", datetime.timedelta(hours=4)),
        Interval.interval_8h: ("8h", datetime.timedelta(hours=8)),
        Interval.interval_1d: ("1d", datetime.timedelta(days=1)),
    }

    def __init__(self, cache_kwargs={"disabled": False, "refresh": False}, log_level: str = "DEBUG"):
        super().__init__(cache_kwargs=cache_kwargs, log_level=log_level)
        self.init_dispatchers()
        self.init_instrument_info_interface()
        self.init_ohlcv_interface()
        self.init_order_book_interface()

    def init_dispatchers(self):
        # Check which endpoints employ a limit
        self.logger.debug("initializing dispatchers")
        self.perpetual_dispatcher = Dispatcher(f"{self.name}.dispatcher.perpetual", timeout=1 / 300)
        self.spot_dispatcher = Dispatcher(f"{self.name}.dispatcher.spot", timeout=1 / 200)

    def init_instrument_info_interface(self):
        perpetual = InstrumentInfoInterface(
            exchange=self,
            interface_name=Interface.INSTRUMENT_INFO,
            inst_type=InstrumentType.PERPETUAL,
            url=os.path.join(self.base_url, "futures/usdt/contracts"),
            dispatcher=self.perpetual_dispatcher,
            execute=instrument_info_perp,
        )

        spot = InstrumentInfoInterface(
            exchange=self,
            interface_name=Interface.INSTRUMENT_INFO,
            inst_type=InstrumentType.SPOT,
            url=os.path.join(self.base_url, "spot/currency_pairs"),
            dispatcher=self.spot_dispatcher,
            execute=instrument_info_spot,
        )

        self.interfaces[Interface.INSTRUMENT_INFO] = {
            InstrumentType.PERPETUAL: perpetual,
            InstrumentType.SPOT: spot,
        }

    def init_ohlcv_interface(self):
        perpetual = OHLCVInterface(
            intervals=self.intervals,
            start_inclusive=True,
            end_inclusive=True,
            max_response_limit=2000,
            exchange=self,
            interface_name=Interface.OHLCV,
            inst_type=InstrumentType.PERPETUAL,
            url=os.path.join(self.base_url, "futures/usdt/candlesticks"),
            dispatcher=self.perpetual_dispatcher,
            execute=ohlcv_perp,
        )

        spot = OHLCVInterface(
            intervals=self.intervals,
            start_inclusive=True,
            end_inclusive=True,
            max_response_limit=1000,
            exchange=self,
            interface_name=Interface.OHLCV,
            inst_type=InstrumentType.SPOT,
            url=os.path.join(self.base_url, "spot/candlesticks"),
            dispatcher=self.spot_dispatcher,
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
            url=os.path.join(self.base_url, "futures/usdt/order_book"),
            dispatcher=self.perpetual_dispatcher,
            execute=order_book_perp,
        )

        spot = OrderBookInterface(
            exchange=self,
            interface_name=Interface.ORDER_BOOK,
            inst_type=InstrumentType.SPOT,
            url=os.path.join(self.base_url, "spot/order_book"),
            dispatcher=self.spot_dispatcher,
            execute=order_book_spot,
        )

        self.interfaces[Interface.ORDER_BOOK] = {
            InstrumentType.PERPETUAL: perpetual,
            InstrumentType.SPOT: spot,
        }


_exchange_export = GateIO
