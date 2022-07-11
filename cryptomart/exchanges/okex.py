import datetime
import os
from typing import List

import pandas as pd
from requests import Request

from ..enums import FundingRateSchema, Instrument, InstrumentType, Interface, Interval, OrderBookSchema
from ..errors import MissingDataError
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

    data = InstrumentInfoInterface.extract_response_data(response, ["data"], ["code"], "0", ["msg"], col_map)
    data = data[data.state == "live"]
    data = data[data.ctType == "linear"]
    data = data[data.settleCcy == "USDT"]
    return data


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

    data = InstrumentInfoInterface.extract_response_data(response, ["data"], ["code"], "0", ["msg"], col_map)
    data = data[data.state == "live"]
    data = data[data.quoteCcy == "USDT"]
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
    data = pd.DataFrame()
    for response in responses:
        try:
            data = pd.concat(
                [data, OHLCVInterface.extract_response_data(response, ["data"], ["code"], "0", ["msg"], col_map)],
                ignore_index=True,
            )
        except MissingDataError:
            continue
    return data


def funding_rate(
    dispatcher: Dispatcher,
    url: str,
    instrument_id: str,
    starttimes: List[datetime.datetime],
    endtimes: List[datetime.datetime],
    limits: List[int],
):
    col_map = {
        "fundingTime": FundingRateSchema.timestamp,
        "fundingRate": FundingRateSchema.funding_rate,
    }
    reqs = []
    for starttime, endtime, limit in zip(starttimes, endtimes, limits):
        req = Request(
            "GET",
            url,
            params={
                "instId": instrument_id,
                "before": dt_to_timestamp(starttime, granularity="milliseconds"),
                "after": dt_to_timestamp(endtime, granularity="milliseconds"),
                "limit": limit,
            },
        )
        reqs.append(req)

    responses = dispatcher.send_requests(reqs)
    data = pd.DataFrame()
    for response in responses:
        try:
            data = pd.concat(
                [
                    data,
                    FundingRateInterface.extract_response_data(response, ["data"], ["code"], "0", ["msg"], col_map),
                ],
                ignore_index=True,
            )
        except MissingDataError:
            continue
    return data


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
    data = OrderBookInterface.extract_response_data(
        response, ["data", 0], ["code"], "0", ["msg"], col_map, ("bids", "asks")
    )
    return data


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

    def __init__(
        self,
        cache_kwargs={"disabled": False, "refresh": False},
        log_level: str = "INFO",
        refresh_instruments: bool = False,
    ):
        super().__init__(cache_kwargs=cache_kwargs, log_level=log_level)
        self.init_dispatchers()
        self.init_instrument_info_interface()
        self.init_ohlcv_interface(refresh_instruments)
        self.init_funding_rate_interface(refresh_instruments)
        self.init_order_book_interface(refresh_instruments)

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

    def init_ohlcv_interface(self, refresh_instruments):
        perpetual = OHLCVInterface(
            refresh_instruments,
            intervals=self.intervals,
            max_response_limit=100,
            exchange=self,
            interface_name=Interface.OHLCV,
            inst_type=InstrumentType.PERPETUAL,
            url=os.path.join(self.base_url, "api/v5/market/history-candles"),
            dispatcher=self.dispatcher,
            execute=ohlcv,
        )

        spot = OHLCVInterface(
            refresh_instruments,
            intervals=self.intervals,
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

    def init_funding_rate_interface(self, refresh_instruments):
        perpetual = FundingRateInterface(
            refresh_instruments,
            max_response_limit=100,
            exchange=self,
            interface_name=Interface.FUNDING_RATE,
            inst_type=InstrumentType.PERPETUAL,
            url=os.path.join(self.base_url, "api/v5/public/funding-rate-history"),
            dispatcher=self.dispatcher,
            execute=funding_rate,
        )

        self.interfaces[Interface.FUNDING_RATE] = {InstrumentType.PERPETUAL: perpetual}

    def init_order_book_interface(self, refresh_instruments):
        perpetual = OrderBookInterface(
            refresh_instruments,
            exchange=self,
            interface_name=Interface.ORDER_BOOK,
            inst_type=InstrumentType.PERPETUAL,
            url=os.path.join(self.base_url, "api/v5/market/books"),
            dispatcher=self.dispatcher,
            execute=order_book,
        )

        spot = OrderBookInterface(
            refresh_instruments,
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
