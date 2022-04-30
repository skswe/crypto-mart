import datetime
import logging
import os

import numpy as np
import pandas as pd
from pyutil.cache import cached
from requests import Request, get

from ..enums import Interval, OrderBookSchema, OrderBookSide
from ..feeds import OHLCVColumn
from .base import ExchangeAPIBase
from .instrument_names.okex import instrument_names as okex_instrument_names

logger = logging.getLogger(__name__)


class OKEx(ExchangeAPIBase):
    name = "okex"

    instrument_names = {**okex_instrument_names}

    intervals = {
        Interval.interval_1h: ("1H", datetime.timedelta(hours=1)),
        Interval.interval_2h: ("2H", datetime.timedelta(hours=2)),
        Interval.interval_4h: ("4H", datetime.timedelta(hours=4)),
        Interval.interval_6h: ("6Hutc", datetime.timedelta(hours=6)),
        Interval.interval_12h: ("12Hutc", datetime.timedelta(hours=12)),
        Interval.interval_1d: ("1Dutc", datetime.timedelta(days=1)),
    }

    @property
    def fee_pct(self):
        return 0.0005

    _base_url = "https://www.okex.com/api/v5"
    _max_requests_per_second = 5
    _limit = 100
    _start_inclusive = False
    _end_inclusive = True
    _ohlcv_column_map = {
        0: OHLCVColumn.open_time,
        1: OHLCVColumn.open,
        2: OHLCVColumn.high,
        3: OHLCVColumn.low,
        4: OHLCVColumn.close,
        6: OHLCVColumn.volume,
    }

    def _ohlcv_prepare_request(self, instType, symbol, interval, starttime, endtime, limit):
        url = "market/history-candles"
        params = {
            "instId": symbol,
            "bar": interval,
            "before": starttime,
            "after": endtime,
            "limit": limit,
        }
        request_url = os.path.join(self._base_url, url)
        return Request("GET", request_url, params=params)

    def _ohlcv_extract_response(self, response):
        if int(response["code"]) != 0:
            # Error has occured

            # Raise general exception for now
            # TODO: build exception handling where reponse error can be fixed
            raise Exception(response["msg"])

        return np.flip(response["data"], axis=0)

    def _order_book_prepare_request(self, instType, symbol, depth=250):
        request_url = os.path.join(self._base_url, "market/books")

        return Request(
            "GET",
            request_url,
            params={
                "instId": symbol,
                "sz": depth,
            },
        )

    def _order_book_extract_response(self, response):
        if int(response["code"]) != 0:
            # Error has occured

            # Raise general exception for now
            # TODO: build exception handling where reponse error can be fixed
            raise Exception(response["msg"])

        response = response["data"][0]
        bids = (
            pd.DataFrame(
                response["bids"], columns=[OrderBookSchema.price, OrderBookSchema.quantity, "liqOrders", "orders"]
            )
            .drop(columns=["liqOrders", "orders"])
            .assign(**{OrderBookSchema.side: OrderBookSide.bid})
        )
        asks = (
            pd.DataFrame(
                response["asks"], columns=[OrderBookSchema.price, OrderBookSchema.quantity, "liqOrders", "orders"]
            )
            .drop(columns=["liqOrders", "orders"])
            .assign(**{OrderBookSchema.side: OrderBookSide.ask})
        )
        df = bids.merge(asks, how="outer").assign(
            **{OrderBookSchema.timestamp: self.ET_to_datetime(response["ts"]).replace(microsecond=0)}
        )
        return df

    @cached("cache/order_book_multiplier", is_method=True, instance_identifiers=["name"], log_level="DEBUG")
    def _order_book_quantity_multiplier(self, instType, symbol, **kwargs):
        if instType == "perpetual":
            _instType = "SWAP"
        else:
            _instType = "FUTURES"
        request_url = os.path.join(self._base_url, f"public/instruments")
        params = {
            "instType": _instType,
            "symbol": symbol,
        }
        res = get(request_url, params).json()
        multiplier = int(res["data"][0]["ctVal"])
        return multiplier


_exchange_export = OKEx
