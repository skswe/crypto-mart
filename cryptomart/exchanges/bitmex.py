import datetime
import json
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
        "underlying": Instrument.cryptomart_symbol,
        "symbol": Instrument.exchange_symbol,
        "listing": Instrument.exchange_list_time,
    }
    params = {
        "filter": json.dumps(
            {
                "typ": "FFWCSX",
                "state": "Open",
                "quoteCurrency": "USDT",
            }
        )
    }
    request = Request("GET", url, params=params)
    response = dispatcher.send_request(request)
    df = InstrumentInfoInterface.handle_response(response, [], [], None, ["error", "message"], col_map)
    return df


def instrument_info_spot(dispatcher: Dispatcher, url: str) -> pd.DataFrame:
    col_map = {
        "underlying": Instrument.cryptomart_symbol,
        "symbol": Instrument.exchange_symbol,
        "listing": Instrument.exchange_list_time,
    }
    params = {
        "filter": json.dumps(
            {
                "typ": "IFXXXP",
                "state": "Open",
                "quoteCurrency": "USDT",
            }
        )
    }
    request = Request("GET", url, params=params)
    response = dispatcher.send_request(request)
    df = InstrumentInfoInterface.handle_response(response, [], [], None, ["error", "message"], col_map)
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
        "timestamp": OHLCVColumn.open_time,
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
                "binSize": interval_id,
                "count": limit,
                "startTime": dt_to_timestamp(starttime, string=True),
                "endTime": dt_to_timestamp(endtime, string=True),
            },
        )
        reqs.append(req)

    responses = dispatcher.send_requests(reqs)
    return OHLCVInterface.format_responses(responses, [], [], None, ["error", "message"], col_map)


def order_book(dispatcher: Dispatcher, url: str, instrument_id: str, depth: int = 20) -> pd.DataFrame:
    col_map = {
        "price": OrderBookSchema.price,
        "size": OrderBookSchema.quantity,
        "side": OrderBookSchema.side,
    }
    request = Request(
        "GET",
        url,
        params={
            "symbol": instrument_id,
            "depth": depth,
        },
    )
    response = dispatcher.send_request(request)
    orderbook = OrderBookInterface.handle_response(response, [], [], None, ["error", "message"], col_map, ())
    orderbook.replace("Sell", OrderBookSide.ask, inplace=True)
    orderbook.replace("Buy", OrderBookSide.bid, inplace=True)
    return orderbook


class BitMEX(ExchangeAPIBase):

    name = "bitmex"
    base_url = "https://www.bitmex.com/api/v1"

    intervals = {
        Interval.interval_1m: ("1m", datetime.timedelta(minutes=1)),
        Interval.interval_5m: ("5m", datetime.timedelta(minutes=5)),
        Interval.interval_1h: ("1h", datetime.timedelta(hours=1)),
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
        self.dispatcher = Dispatcher(f"{self.name}.dispatcher", timeout=1 / 2)

    def init_instrument_info_interface(self):
        perpetual = InstrumentInfoInterface(
            exchange=self,
            interface_name=Interface.INSTRUMENT_INFO,
            inst_type=InstrumentType.PERPETUAL,
            url=os.path.join(self.base_url, "instrument"),
            dispatcher=self.dispatcher,
            execute=instrument_info_perp,
        )

        spot = InstrumentInfoInterface(
            exchange=self,
            interface_name=Interface.INSTRUMENT_INFO,
            inst_type=InstrumentType.SPOT,
            url=os.path.join(self.base_url, "instrument"),
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
            max_response_limit=1000,
            exchange=self,
            interface_name=Interface.OHLCV,
            inst_type=InstrumentType.PERPETUAL,
            url=os.path.join(self.base_url, "trade/bucketed"),
            dispatcher=self.dispatcher,
            execute=ohlcv,
        )

        spot = OHLCVInterface(
            intervals=self.intervals,
            start_inclusive=True,
            end_inclusive=True,
            max_response_limit=1000,
            exchange=self,
            interface_name=Interface.OHLCV,
            inst_type=InstrumentType.SPOT,
            url=os.path.join(self.base_url, "trade/bucketed"),
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
            url=os.path.join(self.base_url, "orderBook/L2"),
            dispatcher=self.dispatcher,
            execute=order_book,
        )

        spot = OrderBookInterface(
            exchange=self,
            interface_name=Interface.ORDER_BOOK,
            inst_type=InstrumentType.SPOT,
            url=os.path.join(self.base_url, "orderBook/L2"),
            dispatcher=self.dispatcher,
            execute=order_book,
        )

        self.interfaces[Interface.ORDER_BOOK] = {
            InstrumentType.PERPETUAL: perpetual,
            InstrumentType.SPOT: spot,
        }


_exchange_export = BitMEX
