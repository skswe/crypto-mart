import datetime
import logging
import os

import pandas as pd
from pyutil.cache import cached
from requests import Request, get

from ..enums import FundingRateSchema, Interval, OrderBookSchema, OrderBookSide
from ..feeds import OHLCVColumn
from .base import ExchangeAPIBase
from .instrument_names.kucoin import instrument_names as kucoin_instrument_names

logger = logging.getLogger(__name__)


class Kucoin(ExchangeAPIBase):
    name = "kucoin"

    instrument_names = {**kucoin_instrument_names}

    intervals = {
        Interval.interval_1m: (1, datetime.timedelta(minutes=1)),
        Interval.interval_5m: (5, datetime.timedelta(minutes=5)),
        Interval.interval_15m: (15, datetime.timedelta(minutes=15)),
        Interval.interval_30m: (30, datetime.timedelta(minutes=30)),
        Interval.interval_1h: (60, datetime.timedelta(hours=1)),
        Interval.interval_2h: (120, datetime.timedelta(hours=2)),
        Interval.interval_4h: (240, datetime.timedelta(hours=4)),
        Interval.interval_8h: (480, datetime.timedelta(hours=8)),
        Interval.interval_12h: (720, datetime.timedelta(hours=12)),
        Interval.interval_1d: (1440, datetime.timedelta(days=1)),
    }

    _base_url = "https://api-futures.kucoin.com/api/v1"
    _max_requests_per_second = 10
    _ohlcv_limit = 200
    _funding_rate_limit = 200
    _start_inclusive = True
    _end_inclusive = True
    _ohlcv_column_map = {
        0: OHLCVColumn.open_time,
        1: OHLCVColumn.open,
        2: OHLCVColumn.high,
        3: OHLCVColumn.low,
        4: OHLCVColumn.close,
        5: OHLCVColumn.volume,
    }
    _funding_rate_column_map = {
        "timesPoint": FundingRateSchema.timestamp,
        "fundingRate": FundingRateSchema.funding_rate,
    }

    def _ohlcv_prepare_request(self, symbol, instType, interval, starttime, endtime, limit):
        url = "kline/query"
        params = {
            "symbol": symbol,
            "granularity": interval,
            "from": starttime,
            "to": endtime,
        }
        request_url = os.path.join(self._base_url, url)
        return Request("GET", request_url, params=params)

    def _ohlcv_extract_response(self, response):
        if response["code"] != "200000":
            # Error has occured

            # Raise general exception for now
            # TODO: build exception handling where reponse error can be fixed
            raise Exception(response["msg"])
        return response["data"]

    def _order_book_prepare_request(self, symbol, instType, depth):
        request_url = os.path.join(self._base_url, "level2/depth100")

        return Request(
            "GET",
            request_url,
            params={
                "symbol": symbol,
            },
        )

    def _order_book_extract_response(self, response):
        if response["code"] != "200000":
            # Error has occured

            # Raise general exception for now
            # TODO: build exception handling where reponse error can be fixed
            raise Exception(response["msg"])
        response = response["data"]
        bids = pd.DataFrame(response["bids"], columns=[OrderBookSchema.price, OrderBookSchema.quantity]).assign(
            **{OrderBookSchema.side: OrderBookSide.bid}
        )
        asks = pd.DataFrame(response["asks"], columns=[OrderBookSchema.price, OrderBookSchema.quantity]).assign(
            **{OrderBookSchema.side: OrderBookSide.ask}
        )
        df = bids.merge(asks, how="outer").assign(
            **{OrderBookSchema.timestamp: self.ET_to_datetime(response["ts"] / 1e6).replace(microsecond=0)}
        )
        return df

    @cached("/tmp/cache/order_book_multiplier", is_method=True, instance_identifiers=["name"], log_level="DEBUG")
    def _order_book_quantity_multiplier(self, symbol, instType, **kwargs):
        request_url = os.path.join(self._base_url, f"contracts/{symbol}")
        res = get(request_url).json()
        return float(res["data"]["multiplier"])

    def _histrorical_funding_rate_prepare_request(self, instType, symbol, starttime, endtime, limit):
        request_url = os.path.join(self._base_url, "funding-history")
        print(request_url)
        params = {
            "symbol": "XBTUSDM",
            # "startAt": starttime,
            # "endAt": endtime,
        }
        print(params)
        return Request(
            "GET",
            request_url,
            params=params,
        )

    def _histrorical_funding_rate_extract_response(self, response):
        print(response)
        if response["code"] != "200000":
            # Error has occured

            # Raise general exception for now
            # TODO: build exception handling where reponse error can be fixed
            raise Exception(response["msg"])
        return response["dataList"]


_exchange_export = Kucoin
