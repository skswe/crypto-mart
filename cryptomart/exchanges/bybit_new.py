import datetime
import os
from typing import List

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


def instrument_info(dispatcher: Dispatcher, url: str) -> pd.DataFrame:
    request = Request("GET", url)
    response = dispatcher.send_request(request)

    data = response["result"]

    data = pd.DataFrame(data)
    data = data[data.status == "TRADING"]

    # filter out symbols that end in a number
    data = data[data.name.apply(lambda e: e[-1] not in [str(x) for x in range(0, 9)])]
    data = data[data.quote_currency == "USDT"]

    data[Instrument.cryptomart_symbol] = data["base_currency"]
    data[Instrument.exchange_symbol] = data["name"]
    return data


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
                "from": dt_to_timestamp(starttime, seconds=True),
                "limit": limit,
            },
        )
        reqs.append(req)

    responses = dispatcher.send_requests(reqs)
    out = pd.DataFrame(columns=col_map.values())

    for res in responses:
        if res["ret_msg"] != "OK":
            raise Exception(res["ret_msg"])

        res = res["result"]
        if len(res) == 0:
            return out
        data: pd.DataFrame = pd.DataFrame(data)
        data.rename(columns=col_map, inplace=True)
        data = data[col_map.values()]
        out = pd.concat([out, data], ignore_index=True)
    out[OHLCVColumn.open_time] = out[OHLCVColumn.open_time].astype(int)
    return out.sort_values(OHLCVColumn.open_time, ascending=True)


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
                "startTime": dt_to_timestamp(starttime, seconds=True),
                "endTime": dt_to_timestamp(endtime, seconds=True),
                "limit": limit,
            },
        )
        reqs.append(req)

    responses = dispatcher.send_requests(reqs)
    out = pd.DataFrame(columns=col_map.values())

    for res in responses:
        if res["ret_msg"] != "OK":
            raise Exception(res["ret_msg"])

        res = res["result"]
        if len(res) == 0:
            return out
        data = np.array(res)[:, list(col_map.keys())]
        data = pd.DataFrame(data, columns=list(col_map.values()))
        out = pd.concat([out, data], ignore_index=True)
    out[OHLCVColumn.open_time] = out[OHLCVColumn.open_time].astype(int)
    return out.sort_values(OHLCVColumn.open_time, ascending=True)


def order_book(dispatcher: Dispatcher, url: str, instrument_name: str, depth: int = 20) -> pd.DataFrame:
    request = Request(
        "GET",
        url,
        params={
            "symbol": instrument_name,
        },
    )

    response = dispatcher.send_request(request)

    if response["result"] == None:
        raise Exception("No data for this symbol")

    orderbook = (
        pd.DataFrame(response["result"])
        .drop(columns=["symbol"])
        .reindex(columns=[OrderBookSchema.price, "size", OrderBookSchema.side])
        .rename(columns={"size": OrderBookSchema.quantity})
        .replace(["Sell", "Buy"], [OrderBookSide.ask, OrderBookSide.bid])
        .assign(**{OrderBookSchema.timestamp: datetime.datetime.utcnow()})
    )
    return orderbook


class Bybit(ExchangeAPIBase):

    name = "bybit"
    base_url = "https://api.bybit.com"

    intervals = {
        Interval.interval_1m: (1, datetime.timedelta(minutes=1)),
        Interval.interval_5m: (5, datetime.timedelta(minutes=5)),
        Interval.interval_15m: (15, datetime.timedelta(minutes=15)),
        Interval.interval_1h: (60, datetime.timedelta(hours=1)),
        Interval.interval_4h: (240, datetime.timedelta(hours=4)),
        Interval.interval_12h: (720, datetime.timedelta(hours=12)),
        Interval.interval_1d: ("D", datetime.timedelta(days=1)),
    }

    def __init__(self, cache_kwargs={"disabled": False, "refresh": False}):
        super().__init__(cache_kwargs=cache_kwargs)
        self.init_dispatchers()
        self.init_instrument_info_interface()
        self.init_instruments()
        self.init_ohlcv_interface()
        self.init_order_book_interface()

    def init_dispatchers(self):
        # Check which endpoints employ a limit
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
