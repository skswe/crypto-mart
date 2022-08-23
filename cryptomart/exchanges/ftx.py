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
        "underlying": Instrument.cryptomart_symbol,
        "name": Instrument.exchange_symbol,
    }
    request = Request("GET", url)
    response = dispatcher.send_request(request)
    data = InstrumentInfoInterface.extract_response_data(response, ["result"], ["success"], True, ["error"], col_map)
    data = data[data.enabled]
    data = data[data.type == "future"]
    data = data[~data.isEtfMarket]
    data = data[~data.restricted]

    data = data[data.name.apply(lambda e: e.endswith("PERP"))]
    return data


def instrument_info_spot(dispatcher: Dispatcher, url: str) -> pd.DataFrame:
    col_map = {
        "baseCurrency": Instrument.cryptomart_symbol,
        "name": Instrument.exchange_symbol,
    }
    request = Request("GET", url)
    response = dispatcher.send_request(request)
    data = InstrumentInfoInterface.extract_response_data(response, ["result"], ["success"], True, ["error"], col_map)
    data = data[data.enabled]
    data = data[data.type == "spot"]
    data = data[~data.isEtfMarket]
    data = data[~data.restricted]

    data = data[data.quoteCurrency == "USD"]
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
        "startTime": OHLCVColumn.open_time,
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
            url.format(symbol=instrument_id),
            params={
                "resolution": interval_id,
                "start_time": dt_to_timestamp(starttime, granularity="seconds"),
                "end_time": dt_to_timestamp(endtime, granularity="seconds"),
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
                    OHLCVInterface.extract_response_data(response, ["result"], ["success"], True, ["error"], col_map),
                ],
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
        "time": FundingRateSchema.timestamp,
        "rate": FundingRateSchema.funding_rate,
    }
    reqs = []
    for starttime, endtime, limit in zip(starttimes, endtimes, limits):
        req = Request(
            "GET",
            url,
            params={
                "future": instrument_id,
                "start_time": dt_to_timestamp(starttime, granularity="seconds"),
                "end_time": dt_to_timestamp(endtime, granularity="seconds"),
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
                    FundingRateInterface.extract_response_data(
                        response, ["result"], ["success"], True, ["error"], col_map
                    ),
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
        url.format(symbol=instrument_id),
        params={
            "depth": depth,
        },
    )
    response = dispatcher.send_request(request)
    data = OrderBookInterface.extract_response_data(
        response, ["result"], ["success"], True, ["error"], col_map, ("bids", "asks")
    )
    return data


class FTX(ExchangeAPIBase):

    name = "ftx"
    base_url = "https://ftx.com/api"

    intervals = {
        Interval.interval_1m: (60, datetime.timedelta(minutes=1)),
        Interval.interval_5m: (300, datetime.timedelta(minutes=5)),
        Interval.interval_15m: (900, datetime.timedelta(minutes=15)),
        Interval.interval_1h: (3600, datetime.timedelta(hours=1)),
        Interval.interval_1d: (86400, datetime.timedelta(days=1)),
    }

    def __init__(
        self,
        cache_kwargs={"disabled": False, "refresh": False},
        log_level: str = "INFO",
        refresh_instruments: bool = False,
    ):
        super().__init__(cache_kwargs=cache_kwargs, log_level=log_level)
        self.init_dispatchers()
        self.init_instrument_info_interface(refresh_instruments)
        self.init_ohlcv_interface()
        self.init_funding_rate_interface()
        self.init_order_book_interface()

    def init_dispatchers(self):
        self.logger.debug("initializing dispatchers")
        self.dispatcher = Dispatcher(f"{self.name}.dispatcher", timeout=1 / 7)

    def init_instrument_info_interface(self, refresh):
        perpetual = InstrumentInfoInterface(
            exchange=self,
            interface_name=Interface.INSTRUMENT_INFO,
            inst_type=InstrumentType.PERPETUAL,
            url=os.path.join(self.base_url, "markets"),
            dispatcher=self.dispatcher,
            execute=instrument_info_perp,
        )

        spot = InstrumentInfoInterface(
            exchange=self,
            interface_name=Interface.INSTRUMENT_INFO,
            inst_type=InstrumentType.SPOT,
            url=os.path.join(self.base_url, "markets"),
            dispatcher=self.dispatcher,
            execute=instrument_info_spot,
        )

        self.perpetual_instruments = perpetual.run(
            map_column=Instrument.exchange_symbol, cache_kwargs={"refresh": refresh}
        )
        self.spot_instruments = spot.run(map_column=Instrument.exchange_symbol, cache_kwargs={"refresh": refresh})
        self.perpetual_order_book_multis = perpetual.run(
            map_column=Instrument.orderbook_multi, cache_kwargs={"refresh": refresh}
        )
        self.spot_order_book_multis = spot.run(
            map_column=Instrument.orderbook_multi, cache_kwargs={"refresh": refresh}
        )

        self.interfaces[Interface.INSTRUMENT_INFO] = {
            InstrumentType.PERPETUAL: perpetual,
            InstrumentType.SPOT: spot,
        }

    def init_ohlcv_interface(self):
        perpetual = OHLCVInterface(
            instruments=self.perpetual_instruments,
            intervals=self.intervals,
            max_response_limit=1500,
            exchange=self,
            interface_name=Interface.OHLCV,
            inst_type=InstrumentType.PERPETUAL,
            url=os.path.join(self.base_url, "markets/{symbol}/candles"),
            dispatcher=self.dispatcher,
            execute=ohlcv,
        )

        spot = OHLCVInterface(
            instruments=self.spot_instruments,
            intervals=self.intervals,
            max_response_limit=1500,
            exchange=self,
            interface_name=Interface.OHLCV,
            inst_type=InstrumentType.SPOT,
            url=os.path.join(self.base_url, "markets/{symbol}/candles"),
            dispatcher=self.dispatcher,
            execute=ohlcv,
        )

        self.interfaces[Interface.OHLCV] = {
            InstrumentType.PERPETUAL: perpetual,
            InstrumentType.SPOT: spot,
        }

    def init_funding_rate_interface(self):
        perpetual = FundingRateInterface(
            instruments=self.perpetual_instruments,
            max_response_limit=500,
            funding_interval=datetime.timedelta(hours=1),
            exchange=self,
            interface_name=Interface.FUNDING_RATE,
            inst_type=InstrumentType.PERPETUAL,
            url=os.path.join(self.base_url, "funding_rates"),
            dispatcher=self.dispatcher,
            execute=funding_rate,
        )

        self.interfaces[Interface.FUNDING_RATE] = {InstrumentType.PERPETUAL: perpetual}

    def init_order_book_interface(self):
        perpetual = OrderBookInterface(
            instruments=self.perpetual_instruments,
            multipliers=self.perpetual_order_book_multis,
            exchange=self,
            interface_name=Interface.ORDER_BOOK,
            inst_type=InstrumentType.PERPETUAL,
            url=os.path.join(self.base_url, "markets/{symbol}/orderbook"),
            dispatcher=self.dispatcher,
            execute=order_book,
        )

        spot = OrderBookInterface(
            instruments=self.spot_instruments,
            multipliers=self.spot_order_book_multis,
            exchange=self,
            interface_name=Interface.ORDER_BOOK,
            inst_type=InstrumentType.SPOT,
            url=os.path.join(self.base_url, "markets/{symbol}/orderbook"),
            dispatcher=self.dispatcher,
            execute=order_book,
        )

        self.interfaces[Interface.ORDER_BOOK] = {
            InstrumentType.PERPETUAL: perpetual,
            InstrumentType.SPOT: spot,
        }


_exchange_export = FTX
