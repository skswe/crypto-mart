import datetime
import os
from typing import List
from black import json

import numpy as np
import pandas as pd
from cryptomart.interfaces.instrument_info import InstrumentInfoInterface
from cryptomart.interfaces.order_book import OrderBookInterface
from requests import Request

from ..enums import Instrument, InstrumentType, Interface, Interval, OrderBookSchema, OrderBookSide
from ..feeds import OHLCVColumn
from ..interfaces.ohlcv import OHLCVInterface
from ..types import IntervalType
from ..util import Dispatcher, dt_to_timestamp, parse_time
from .base import ExchangeAPIBase


def instrument_info_perp(dispatcher: Dispatcher, url: str) -> pd.DataFrame:
    filter = {
        "typ": "FFWCSX",
        "state": "Open",
        "quoteCurrency": "USDT",
    }

    request = Request("GET", url, params={"filter": json.dumps(filter)})
    response = dispatcher.send_request(request)

    data = pd.DataFrame(response)

    data[Instrument.cryptomart_symbol] = data["underlying"]
    data[Instrument.exchange_symbol] = data["symbol"]

    return data


def instrument_info_spot(dispatcher: Dispatcher, url: str) -> pd.DataFrame:
    filter = {
        "typ": "IFXXXP",
        "state": "Open",
        "quoteCurrency": "USDT",
    }

    request = Request("GET", url, params={"filter": json.dumps(filter)})
    response = dispatcher.send_request(request)

    data = pd.DataFrame(response)

    data[Instrument.cryptomart_symbol] = data["underlying"]
    data[Instrument.exchange_symbol] = data["symbol"]

    return data


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
                "interval": interval_id,
                "startTime": dt_to_timestamp(starttime, milliseconds=True),
                "endTime": dt_to_timestamp(endtime, milliseconds=True),
                "limit": limit,
            },
        )
        reqs.append(req)

    responses = dispatcher.send_requests(reqs)
    out = pd.DataFrame(columns=col_map.values())

    for res in responses:
        if isinstance(res, dict):
            raise Exception(res["error"]["message"])
        if len(res) == 0:
            continue
        data: pd.DataFrame = pd.DataFrame(data)
        data.rename(columns=col_map, inplace=True)
        data = data[col_map.values()]
        out = pd.concat([out, data], ignore_index=True)
    out[OHLCVColumn.open_time] = out[OHLCVColumn.open_time].astype(int)
    return out.sort_values(OHLCVColumn.open_time, ascending=True)


def order_book(dispatcher: Dispatcher, url: str, instrument_name: str, depth: int = 20) -> pd.DataFrame:
    request = Request(
        "GET",
        url,
        params={
            "symbol": instrument_name,
            "limit": depth,
        },
    )

    response = dispatcher.send_request(request)

    if isinstance(response, dict) and "code" in response:
        raise Exception(response["msg"])
    bids = pd.DataFrame(response["bids"], columns=[OrderBookSchema.price, OrderBookSchema.quantity]).assign(
        **{OrderBookSchema.side: OrderBookSide.bid}
    )
    asks = pd.DataFrame(response["asks"], columns=[OrderBookSchema.price, OrderBookSchema.quantity]).assign(
        **{OrderBookSchema.side: OrderBookSide.ask}
    )
    orderbook = bids.merge(asks, how="outer").assign(**{OrderBookSchema.timestamp: datetime.datetime.utcnow()})
    orderbook[OrderBookSchema.timestamp] = orderbook[OrderBookSchema.timestamp].apply(lambda e: parse_time(e))
    return orderbook


class Binance(ExchangeAPIBase):

    name = "binance"
    futures_base_url = "https://fapi.binance.com"
    spot_base_url = "https://api.binance.com"

    intervals = {
        Interval.interval_1m: ("1m", datetime.timedelta(minutes=1)),
        Interval.interval_5m: ("5m", datetime.timedelta(minutes=5)),
        Interval.interval_15m: ("15m", datetime.timedelta(minutes=15)),
        Interval.interval_1h: ("1h", datetime.timedelta(hours=1)),
        Interval.interval_4h: ("4h", datetime.timedelta(hours=4)),
        Interval.interval_8h: ("8h", datetime.timedelta(hours=8)),
        Interval.interval_12h: ("12h", datetime.timedelta(hours=12)),
        Interval.interval_1d: ("1d", datetime.timedelta(days=1)),
        Interval.interval_1w: ("1w", datetime.timedelta(weeks=1)),
    }

    def __init__(self, cache_kwargs={"disabled": False, "refresh": False}):
        super().__init__(cache_kwargs=cache_kwargs)
        self.init_dispatchers()
        self.init_instrument_info_interface()
        self.init_instruments()
        self.init_ohlcv_interface()
        self.init_order_book_interface()

    def init_dispatchers(self):
        self.logger.debug("initializing dispatchers")
        self.perpetual_dispatcher = Dispatcher(f"{self.name}.dispatcher.perpetual", timeout=1 / 4)
        self.spot_dispatcher = Dispatcher(f"{self.name}.dispatcher.spot", timeout=1 / 2)

    def init_instruments(self):
        self.logger.debug("Loading instrument mappings")
        self.perpetual_instruments = self.interfaces[Interface.INSTRUMENT_INFO][InstrumentType.PERPETUAL].run(
            mappings=True, cache_kwargs=self.cache_kwargs
        )
        self.spot_instruments = self.interfaces[Interface.INSTRUMENT_INFO][InstrumentType.SPOT].run(
            mappings=True, cache_kwargs=self.cache_kwargs
        )

    def init_instrument_info_interface(self):
        perpetual = InstrumentInfoInterface(
            exchange=self,
            interface_name=Interface.INSTRUMENT_INFO,
            inst_type=InstrumentType.PERPETUAL,
            url=os.path.join(self.futures_base_url, "fapi/v1/exchangeInfo"),
            dispatcher=self.perpetual_dispatcher,
            execute=instrument_info_perp,
        )

        spot = InstrumentInfoInterface(
            exchange=self,
            interface_name=Interface.INSTRUMENT_INFO,
            inst_type=InstrumentType.SPOT,
            url=os.path.join(self.spot_base_url, "api/v3/exchangeInfo"),
            dispatcher=self.spot_dispatcher,
            execute=instrument_info_spot,
        )

        self.interfaces[Interface.INSTRUMENT_INFO] = {
            InstrumentType.PERPETUAL: perpetual,
            InstrumentType.SPOT: spot,
        }

    def init_ohlcv_interface(self):
        perpetual = OHLCVInterface(
            instruments=self.perpetual_instruments,
            intervals=self.intervals,
            start_inclusive=False,
            end_inclusive=True,
            max_response_limit=1500,
            exchange=self,
            interface_name=Interface.OHLCV,
            inst_type=InstrumentType.PERPETUAL,
            url=os.path.join(self.futures_base_url, "fapi/v1/klines"),
            dispatcher=self.perpetual_dispatcher,
            execute=ohlcv,
        )

        spot = OHLCVInterface(
            instruments=self.spot_instruments,
            intervals=self.intervals,
            start_inclusive=True,
            end_inclusive=True,
            max_response_limit=1000,
            exchange=self,
            interface_name=Interface.OHLCV,
            inst_type=InstrumentType.SPOT,
            url=os.path.join(self.spot_base_url, "api/v3/klines"),
            dispatcher=self.spot_dispatcher,
            execute=ohlcv,
        )

        self.interfaces[Interface.OHLCV] = {
            InstrumentType.PERPETUAL: perpetual,
            InstrumentType.SPOT: spot,
        }

    def init_order_book_interface(self):
        perpetual = OrderBookInterface(
            instruments=self.perpetual_instruments,
            exchange=self,
            interface_name=Interface.ORDER_BOOK,
            inst_type=InstrumentType.PERPETUAL,
            url=os.path.join(self.futures_base_url, "fapi/v1/depth"),
            dispatcher=self.perpetual_dispatcher,
            execute=order_book,
        )

        spot = OrderBookInterface(
            instruments=self.spot_instruments,
            exchange=self,
            interface_name=Interface.ORDER_BOOK,
            inst_type=InstrumentType.SPOT,
            url=os.path.join(self.spot_base_url, "api/v3/depth"),
            dispatcher=self.spot_dispatcher,
            execute=order_book,
        )

        self.interfaces[Interface.ORDER_BOOK] = {
            InstrumentType.PERPETUAL: perpetual,
            InstrumentType.SPOT: spot,
        }


_exchange_export = Binance
