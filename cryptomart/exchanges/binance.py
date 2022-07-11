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
        "baseAsset": Instrument.cryptomart_symbol,
        "symbol": Instrument.exchange_symbol,
        "onboardDate": Instrument.exchange_list_time,
    }
    request = Request("GET", url)
    response = dispatcher.send_request(request)

    data = InstrumentInfoInterface.extract_response_data(response, ["symbols"], [], None, [], col_map)
    data = data[data.status == "TRADING"]
    data = data[data.quoteAsset == "USDT"]
    data = data[data.contractType == "PERPETUAL"]
    return data


def instrument_info_spot(dispatcher: Dispatcher, url: str) -> pd.DataFrame:
    col_map = {
        "baseAsset": Instrument.cryptomart_symbol,
        "symbol": Instrument.exchange_symbol,
    }
    request = Request("GET", url)
    response = dispatcher.send_request(request)

    data = InstrumentInfoInterface.extract_response_data(response, ["symbols"], [], None, [], col_map)
    data = data[data.status == "TRADING"]
    data = data[data.quoteAsset == "USDT"]
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
    data = pd.DataFrame()
    for response in responses:
        try:
            data = pd.concat(
                [data, OHLCVInterface.extract_response_data(response, [], [], None, [], col_map)], ignore_index=True
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
                "symbol": instrument_id,
                "limit": limit,
                "startTime": dt_to_timestamp(starttime, granularity="milliseconds"),
                "endTime": dt_to_timestamp(endtime, granularity="milliseconds"),
            },
        )
        reqs.append(req)

    responses = dispatcher.send_requests(reqs)
    data = pd.DataFrame()
    for response in responses:
        try:
            data = pd.concat(
                [data, FundingRateInterface.extract_response_data(response, [], [], None, [], col_map)],
                ignore_index=True,
            )
        except MissingDataError:
            continue
    return data


def order_book(dispatcher: Dispatcher, url: str, instrument_name: str, depth: int = 20) -> pd.DataFrame:
    col_map = {
        0: OrderBookSchema.price,
        1: OrderBookSchema.quantity,
    }
    request = Request(
        "GET",
        url,
        params={
            "symbol": instrument_name,
            "limit": depth,
        },
    )

    response = dispatcher.send_request(request)
    data = OrderBookInterface.extract_response_data(response, [], [], None, [], col_map, ("bids", "asks"))
    return data


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
        self.perpetual_dispatcher = Dispatcher(f"{self.name}.dispatcher.perpetual", timeout=1 / 4)
        self.spot_dispatcher = Dispatcher(f"{self.name}.dispatcher.spot", timeout=1 / 2)

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

    def init_ohlcv_interface(self, refresh_instruments):
        perpetual = OHLCVInterface(
            refresh_instruments,
            intervals=self.intervals,
            max_response_limit=1500,
            exchange=self,
            interface_name=Interface.OHLCV,
            inst_type=InstrumentType.PERPETUAL,
            url=os.path.join(self.futures_base_url, "fapi/v1/klines"),
            dispatcher=self.perpetual_dispatcher,
            execute=ohlcv,
        )

        spot = OHLCVInterface(
            refresh_instruments,
            intervals=self.intervals,
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

    def init_funding_rate_interface(self, refresh_instruments):
        perpetual = FundingRateInterface(
            refresh_instruments,
            max_response_limit=1000,
            exchange=self,
            interface_name=Interface.FUNDING_RATE,
            inst_type=InstrumentType.PERPETUAL,
            url=os.path.join(self.futures_base_url, "fapi/v1/fundingRate"),
            dispatcher=self.perpetual_dispatcher,
            execute=funding_rate,
        )

        self.interfaces[Interface.FUNDING_RATE] = {InstrumentType.PERPETUAL: perpetual}

    def init_order_book_interface(self, refresh_instruments):
        perpetual = OrderBookInterface(
            refresh_instruments,
            exchange=self,
            interface_name=Interface.ORDER_BOOK,
            inst_type=InstrumentType.PERPETUAL,
            url=os.path.join(self.futures_base_url, "fapi/v1/depth"),
            dispatcher=self.perpetual_dispatcher,
            execute=order_book,
        )

        spot = OrderBookInterface(
            refresh_instruments,
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
