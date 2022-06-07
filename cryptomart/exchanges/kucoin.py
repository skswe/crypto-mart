import base64
import datetime
import hashlib
import hmac
import os
import time
from typing import List

import pandas as pd
from dotenv import load_dotenv
from requests import PreparedRequest, Request

from ..enums import Instrument, InstrumentType, Interface, Interval, OrderBookSchema
from ..feeds import OHLCVColumn
from ..interfaces.funding_rate import FundingRateInterface
from ..interfaces.instrument_info import InstrumentInfoInterface
from ..interfaces.ohlcv import OHLCVInterface
from ..interfaces.order_book import OrderBookInterface
from ..types import IntervalType
from ..util import Dispatcher, dt_to_timestamp
from .base import ExchangeAPIBase

load_dotenv()


def instrument_info_perp(dispatcher: Dispatcher, url: str) -> pd.DataFrame:
    col_map = {
        "baseCurrency": Instrument.cryptomart_symbol,
        "symbol": Instrument.exchange_symbol,
        "firstOpenDate": Instrument.exchange_list_time,
        "multiplier": Instrument.orderbook_multi,
    }
    request = Request("GET", url)
    response = dispatcher.send_request(request)
    df = InstrumentInfoInterface.handle_response(response, ["data"], ["code"], "200000", ["msg"], col_map)
    df = df[df.status == "Open"]
    df = df[df.isInverse == False]
    return df


def instrument_info_spot(dispatcher: Dispatcher, url: str) -> pd.DataFrame:
    col_map = {
        "baseCurrency": Instrument.cryptomart_symbol,
        "symbol": Instrument.exchange_symbol,
    }
    request = Request("GET", url)
    response = dispatcher.send_request(request)
    df = InstrumentInfoInterface.handle_response(response, ["data"], ["code"], "200000", ["msg"], col_map)
    df = df[df.enableTrading == True]
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
                "granularity": interval_id,
                "from": dt_to_timestamp(starttime, granularity="milliseconds"),
                "to": dt_to_timestamp(endtime, granularity="milliseconds"),
            },
        )
        reqs.append(req)

    responses = dispatcher.send_requests(reqs)
    return OHLCVInterface.format_responses(responses, ["data"], ["code"], "200000", ["msg"], col_map)


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
        3: OHLCVColumn.high,
        4: OHLCVColumn.low,
        2: OHLCVColumn.close,
        5: OHLCVColumn.volume,
    }
    reqs = []
    for starttime, endtime, limit in zip(starttimes, endtimes, limits):
        req = Request(
            "GET",
            url,
            params={
                "symbol": instrument_id,
                "type": interval_id,
                "startAt": dt_to_timestamp(starttime, granularity="seconds"),
                "endAt": dt_to_timestamp(endtime, granularity="seconds"),
            },
        )
        reqs.append(req)

    responses = dispatcher.send_requests(reqs)
    return OHLCVInterface.format_responses(responses, ["data"], ["code"], "200000", ["msg"], col_map)


def funding_rate(
    dispatcher: Dispatcher,
    url: str,
    instrument_id: str,
    starttimes: List[datetime.datetime],
    endtimes: List[datetime.datetime],
    limits: List[int],
):
    col_map = {}
    reqs = []
    for starttime, endtime, limit in zip(starttimes, endtimes, limits):
        req = Request(
            "GET",
            url,
            params={},
        )
        reqs.append(req)

    responses = dispatcher.send_requests(reqs)
    return FundingRateInterface.format_responses(responses, [], [], None, [], col_map)


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
        },
    )

    response = dispatcher.send_request(request)
    orderbook = OrderBookInterface.handle_response(
        response, ["data"], ["code"], "200000", ["msg"], col_map, ("bids", "asks")
    )
    return orderbook


def authenticate_request_spot(request: PreparedRequest) -> PreparedRequest:
    API_KEY = os.environ["KUCOIN_SPOT_API_KEY"]
    API_SECRET = os.environ["KUCOIN_SPOT_API_SECRET"]
    API_PASSPHRASE = os.environ["KUCOIN_SPOT_API_PASSPHRASE"]
    now = int(time.time() * 1000)
    str_to_sign = str(now) + request.method + request.path_url + (request.body or "")
    signature = base64.b64encode(
        hmac.new(API_SECRET.encode("utf-8"), str_to_sign.encode("utf-8"), hashlib.sha256).digest()
    )
    passphrase = base64.b64encode(
        hmac.new(API_SECRET.encode("utf-8"), API_PASSPHRASE.encode("utf-8"), hashlib.sha256).digest()
    )
    request.headers = {
        "KC-API-SIGN": signature,
        "KC-API-TIMESTAMP": str(now),
        "KC-API-KEY": API_KEY,
        "KC-API-PASSPHRASE": passphrase,
        "KC-API-KEY-VERSION": "2",
    }
    return request


class Kucoin(ExchangeAPIBase):

    name = "kucoin"
    spot_base_url = "https://api.kucoin.com"
    futures_base_url = "https://api-futures.kucoin.com"

    perpetual_intervals = {
        Interval.interval_1m: (1, datetime.timedelta(minutes=1)),
        Interval.interval_5m: (5, datetime.timedelta(minutes=5)),
        Interval.interval_15m: (15, datetime.timedelta(minutes=15)),
        Interval.interval_1h: (60, datetime.timedelta(hours=1)),
        Interval.interval_4h: (240, datetime.timedelta(hours=4)),
        Interval.interval_8h: (480, datetime.timedelta(hours=8)),
        Interval.interval_12h: (720, datetime.timedelta(hours=12)),
        Interval.interval_1d: (1440, datetime.timedelta(days=1)),
    }

    spot_intervals = {
        Interval.interval_1m: ("1min", datetime.timedelta(minutes=1)),
        Interval.interval_5m: ("5min", datetime.timedelta(minutes=5)),
        Interval.interval_15m: ("15min", datetime.timedelta(minutes=15)),
        Interval.interval_1h: ("1hour", datetime.timedelta(hours=1)),
        Interval.interval_4h: ("4hour", datetime.timedelta(hours=4)),
        Interval.interval_8h: ("8hour", datetime.timedelta(hours=8)),
        Interval.interval_12h: ("12hour", datetime.timedelta(hours=12)),
        Interval.interval_1d: ("1day", datetime.timedelta(days=1)),
    }

    def __init__(self, cache_kwargs={"disabled": False, "refresh": False}, log_level: str = "INFO"):
        super().__init__(cache_kwargs=cache_kwargs, log_level=log_level)
        self.init_dispatchers()
        self.init_instrument_info_interface()
        self.init_ohlcv_interface()
        self.init_order_book_interface()

    def init_dispatchers(self):
        self.logger.debug("initializing dispatchers")
        self.perpetual_dispatcher = Dispatcher(f"{self.name}.dispatcher.perpetual", timeout=1 / 2)
        self.spot_dispatcher = Dispatcher(
            f"{self.name}.dispatcher.spot", timeout=1 / 2, pre_request_hook=authenticate_request_spot
        )

    def init_instrument_info_interface(self):
        perpetual = InstrumentInfoInterface(
            exchange=self,
            interface_name=Interface.INSTRUMENT_INFO,
            inst_type=InstrumentType.PERPETUAL,
            url=os.path.join(self.futures_base_url, "api/v1/contracts/active"),
            dispatcher=self.perpetual_dispatcher,
            execute=instrument_info_perp,
        )

        spot = InstrumentInfoInterface(
            exchange=self,
            interface_name=Interface.INSTRUMENT_INFO,
            inst_type=InstrumentType.SPOT,
            url=os.path.join(self.spot_base_url, "api/v1/symbols"),
            dispatcher=self.spot_dispatcher,
            execute=instrument_info_spot,
        )

        self.interfaces[Interface.INSTRUMENT_INFO] = {
            InstrumentType.PERPETUAL: perpetual,
            InstrumentType.SPOT: spot,
        }

    def init_ohlcv_interface(self):
        perpetual = OHLCVInterface(
            intervals=self.perpetual_intervals,
            start_inclusive=True,
            end_inclusive=True,
            max_response_limit=1500,
            exchange=self,
            interface_name=Interface.OHLCV,
            inst_type=InstrumentType.PERPETUAL,
            url=os.path.join(self.futures_base_url, "api/v1/kline/query"),
            dispatcher=self.perpetual_dispatcher,
            execute=ohlcv_perp,
        )

        spot = OHLCVInterface(
            intervals=self.spot_intervals,
            start_inclusive=True,
            end_inclusive=True,
            max_response_limit=1000,
            exchange=self,
            interface_name=Interface.OHLCV,
            inst_type=InstrumentType.SPOT,
            url=os.path.join(self.spot_base_url, "api/v1/market/candles"),
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
            url=os.path.join(self.futures_base_url, "api/v1/level2/depth100"),
            dispatcher=self.perpetual_dispatcher,
            execute=order_book,
        )

        spot = OrderBookInterface(
            exchange=self,
            interface_name=Interface.ORDER_BOOK,
            inst_type=InstrumentType.SPOT,
            url=os.path.join(self.spot_base_url, "api/v3/market/orderbook/level2"),
            dispatcher=self.spot_dispatcher,
            execute=order_book,
        )

        self.interfaces[Interface.ORDER_BOOK] = {
            InstrumentType.PERPETUAL: perpetual,
            InstrumentType.SPOT: spot,
        }


_exchange_export = Kucoin
