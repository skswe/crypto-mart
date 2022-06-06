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
        "base": Instrument.cryptomart_symbol,
        "marketCode": Instrument.exchange_symbol,
        "listedAt": Instrument.exchange_list_time,
    }
    request = Request("GET", url)
    response = dispatcher.send_request(request)

    df = InstrumentInfoInterface.handle_response(response, ["data"], ["success"], True, [], col_map)
    df = df[df.type == "FUTURE"]
    df = df[df.counter == "USD"]
    df = df[df.settlementAt.isna()]
    return df


def instrument_info_spot(dispatcher: Dispatcher, url: str) -> pd.DataFrame:
    col_map = {
        "base": Instrument.cryptomart_symbol,
        "marketCode": Instrument.exchange_symbol,
        "listedAt": Instrument.exchange_list_time,
    }
    request = Request("GET", url)
    response = dispatcher.send_request(request)

    df = InstrumentInfoInterface.handle_response(response, ["data"], ["success"], True, [], col_map)
    df = df[df.type == "SPOT"]
    df = df[df.counter == "USD"]
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
        "openedAt": OHLCVColumn.open_time,
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
                "marketCode": instrument_id,
                "timeframe": interval_id,
                "startTime": dt_to_timestamp(starttime, granularity="milliseconds"),
                "endTime": dt_to_timestamp(endtime, granularity="milliseconds"),
                "limit": limit,
            },
        )
        reqs.append(req)

    responses = dispatcher.send_requests(reqs)
    return OHLCVInterface.format_responses(responses, ["data"], ["success"], True, ["message"], col_map)


def ohlcv_limit(timedelta: datetime.timedelta) -> int:
    TIME_LIMIT = datetime.timedelta(days=7)
    RECORD_LIMIT = 5000
    return min(RECORD_LIMIT, int(TIME_LIMIT / timedelta))


def order_book(dispatcher: Dispatcher, url: str, instrument_id: str, depth: int = 20) -> pd.DataFrame:
    col_map = {
        0: OrderBookSchema.price,
        1: OrderBookSchema.quantity,
    }
    request = Request(
        "GET",
        url,
        params={
            "marketCode": instrument_id,
            "level": depth,
        },
    )

    response = dispatcher.send_request(request)
    orderbook = OrderBookInterface.handle_response(
        response, ["data"], ["success"], True, ["message"], col_map, ("bids", "asks")
    )
    return orderbook


class CoinFLEX(ExchangeAPIBase):

    name = "coinflex"
    base_url = "https://v2api.coinflex.com"

    intervals = {
        Interval.interval_1m: ("60s", datetime.timedelta(minutes=1)),
        Interval.interval_5m: ("300s", datetime.timedelta(minutes=5)),
        Interval.interval_15m: ("900s", datetime.timedelta(minutes=15)),
        Interval.interval_1h: ("3600s", datetime.timedelta(hours=1)),
        Interval.interval_4h: ("14400s", datetime.timedelta(hours=4)),
        Interval.interval_1d: ("86400s", datetime.timedelta(days=1)),
    }

    def __init__(self, cache_kwargs={"disabled": False, "refresh": False}, log_level: str = "INFO"):
        super().__init__(cache_kwargs=cache_kwargs, log_level=log_level)
        self.init_dispatchers()
        self.init_instrument_info_interface()
        self.init_ohlcv_interface()
        self.init_order_book_interface()

    def init_dispatchers(self):
        self.logger.debug("initializing dispatchers")
        self.dispatcher = Dispatcher(f"{self.name}.dispatcher.perpetual", timeout=1 / 6)

    def init_instrument_info_interface(self):
        perpetual = InstrumentInfoInterface(
            exchange=self,
            interface_name=Interface.INSTRUMENT_INFO,
            inst_type=InstrumentType.PERPETUAL,
            url=os.path.join(self.base_url, "v3/markets"),
            dispatcher=self.dispatcher,
            execute=instrument_info_perp,
        )

        spot = InstrumentInfoInterface(
            exchange=self,
            interface_name=Interface.INSTRUMENT_INFO,
            inst_type=InstrumentType.SPOT,
            url=os.path.join(self.base_url, "v3/markets"),
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
            start_inclusive=True,
            end_inclusive=True,
            max_response_limit=ohlcv_limit,
            exchange=self,
            interface_name=Interface.OHLCV,
            inst_type=InstrumentType.PERPETUAL,
            url=os.path.join(self.base_url, "v3/candles"),
            dispatcher=self.dispatcher,
            execute=ohlcv,
        )

        spot = OHLCVInterface(
            intervals=self.intervals,
            start_inclusive=True,
            end_inclusive=True,
            max_response_limit=ohlcv_limit,
            exchange=self,
            interface_name=Interface.OHLCV,
            inst_type=InstrumentType.SPOT,
            url=os.path.join(self.base_url, "v3/candles"),
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
            url=os.path.join(self.base_url, "v3/depth"),
            dispatcher=self.dispatcher,
            execute=order_book,
        )

        spot = OrderBookInterface(
            exchange=self,
            interface_name=Interface.ORDER_BOOK,
            inst_type=InstrumentType.SPOT,
            url=os.path.join(self.base_url, "v3/depth"),
            dispatcher=self.dispatcher,
            execute=order_book,
        )

        self.interfaces[Interface.ORDER_BOOK] = {
            InstrumentType.PERPETUAL: perpetual,
            InstrumentType.SPOT: spot,
        }


_exchange_export = CoinFLEX
