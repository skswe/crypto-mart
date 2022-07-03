import datetime
import logging
import os
from typing import List

import pandas as pd
from requests import Request

from ..enums import FundingRateSchema, Instrument, InstrumentType, Interface, Interval, OrderBookSchema, OrderBookSide
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
        "name": Instrument.exchange_symbol,
        "quanto_multiplier": Instrument.orderbook_multi,
    }
    request = Request("GET", url)
    response = dispatcher.send_request(request)
    data = InstrumentInfoInterface.extract_response_data(response, [], [], None, ["message"], col_map)
    data[Instrument.cryptomart_symbol] = data.name.apply(lambda e: e.replace("_USDT", ""))

    data = data[data.in_delisting == False]
    data = data[data.type == "direct"]
    return data


def instrument_info_spot(dispatcher: Dispatcher, url: str) -> pd.DataFrame:
    col_map = {
        "base": Instrument.cryptomart_symbol,
        "id": Instrument.exchange_symbol,
    }
    request = Request("GET", url)
    response = dispatcher.send_request(request)
    data = InstrumentInfoInterface.extract_response_data(response, [], [], None, ["message"], col_map)

    data = data[data.trade_status == "tradable"]
    data = data[data.quote == "USDT"]
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
    data = pd.DataFrame()
    for response in responses:
        try:
            data = pd.concat(
                [data, OHLCVInterface.extract_response_data(response, [], [], None, ["message"], col_map)],
                ignore_index=True,
            )
        except MissingDataError:
            continue
    return data


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
    data = pd.DataFrame()
    for response in responses:
        try:
            data = pd.concat(
                [data, OHLCVInterface.extract_response_data(response, [], [], None, ["message"], col_map)],
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
    logger = logging.getLogger("cryptomart.gateio.funding_rate.perpetual")
    logger.warning(
        f"GateIO only returns the latest 1000 datapoints for funding-rate regardless of start and end times."
    )
    col_map = {
        "t": FundingRateSchema.timestamp,
        "r": FundingRateSchema.funding_rate,
    }
    req = Request(
        "GET",
        url,
        params={
            "contract": instrument_id,
            "limit": 1000,
        },
    )
    response = dispatcher.send_request(req)
    data = FundingRateInterface.extract_response_data(response, [], [], None, ["message"], col_map)
    return data


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
    data = OrderBookInterface.extract_response_data(response, [], [], None, ["message"], col_map, ("bids", "asks"))
    return data


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
    data = OrderBookInterface.extract_response_data(response, [], [], None, ["message"], col_map, ("bids", "asks"))
    return data


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

    def __init__(self, cache_kwargs={"disabled": False, "refresh": False}, log_level: str = "INFO"):
        super().__init__(cache_kwargs=cache_kwargs, log_level=log_level)
        self.init_dispatchers()
        self.init_instrument_info_interface()
        self.init_ohlcv_interface()
        self.init_funding_rate_interface()
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
            max_response_limit=995,
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

    def init_funding_rate_interface(self):
        perpetual = FundingRateInterface(
            max_response_limit=1000,
            exchange=self,
            interface_name=Interface.FUNDING_RATE,
            inst_type=InstrumentType.PERPETUAL,
            url=os.path.join(self.base_url, "futures/usdt/funding_rate"),
            dispatcher=self.perpetual_dispatcher,
            execute=funding_rate,
        )

        self.interfaces[Interface.FUNDING_RATE] = {InstrumentType.PERPETUAL: perpetual}

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
