import datetime
import logging
import os

import pandas as pd
from cryptomart.feeds import OHLCVColumn
from requests import Request

from ..enums import Interval, OrderBookSchema, OrderBookSide
from .base import ExchangeAPIBase
from .instrument_names.bybit import instrument_names as bybit_instrument_names

logger = logging.getLogger(__name__)


class Bybit(ExchangeAPIBase):

    name = "bybit"

    instrument_names = {**bybit_instrument_names}

    intervals = {
        Interval.interval_1m: (1, datetime.timedelta(minutes=1)),
        Interval.interval_3m: (3, datetime.timedelta(minutes=3)),
        Interval.interval_5m: (5, datetime.timedelta(minutes=5)),
        Interval.interval_15m: (15, datetime.timedelta(minutes=15)),
        Interval.interval_30m: (30, datetime.timedelta(minutes=30)),
        Interval.interval_1h: (60, datetime.timedelta(hours=1)),
        Interval.interval_2h: (120, datetime.timedelta(hours=2)),
        Interval.interval_4h: (240, datetime.timedelta(hours=4)),
        Interval.interval_6h: (360, datetime.timedelta(hours=6)),
        Interval.interval_12h: (720, datetime.timedelta(hours=12)),
        Interval.interval_1d: ("D", datetime.timedelta(days=1)),
    }

    @property
    def fee_pct(self):
        return 0.0006

    _base_url = "https://api.bybit.com"
    _max_requests_per_second = 40
    _limit = 200
    _start_inclusive = True
    _end_inclusive = False

    _ohlcv_column_map = {
        "open_time": OHLCVColumn.open_time,
        "open": OHLCVColumn.open,
        "high": OHLCVColumn.high,
        "low": OHLCVColumn.low,
        "close": OHLCVColumn.close,
        "volume": OHLCVColumn.volume,
    }

    def _ohlcv_prepare_request(self, instType, symbol, interval, starttime, endtime, limit):
        url = "public/linear/kline"
        params = {
            "symbol": symbol,
            "interval": interval,
            "from": starttime,
            "limit": limit,
        }
        request_url = os.path.join(self._base_url, url)
        return Request("GET", request_url, params=params)

    def _ohlcv_extract_response(self, response):
        if response["ret_msg"] != "OK":
            # Error has occured

            # Raise general exception for now
            # TODO: build exception handling where reponse error can be fixed
            raise Exception(response["ret_msg"])
        return response["result"]

    def _order_book_prepare_request(self, instType, symbol, depth):
        request_url = os.path.join(self._base_url, "v2/public/orderBook/L2")

        return Request(
            "GET",
            request_url,
            params={
                "symbol": symbol,
            },
        )

    def _order_book_extract_response(self, response):
        if response["result"] == None:
            # Error has occured

            # Raise general exception for now
            # TODO: build exception handling where reponse error can be fixed
            raise Exception("No data for this symbol")
        df = (
            pd.DataFrame(response["result"])
            .drop(columns=["symbol"])
            .reindex(columns=[OrderBookSchema.price, "size", OrderBookSchema.side])
            .rename(columns={"size": OrderBookSchema.quantity})
            .replace(["Sell", "Buy"], [OrderBookSide.ask, OrderBookSide.bid])
            .assign(
                **{OrderBookSchema.timestamp: datetime.datetime.utcfromtimestamp(int(float(response["time_now"])))}
            )
        )
        return df

    def _order_book_quantity_multiplier(self, instType, symbol, **kwargs):
        return 1

    @staticmethod
    def ET_to_datetime(et):
        # Convert exchange native time format to datetime
        return datetime.datetime.utcfromtimestamp(int(et))

    @staticmethod
    def datetime_to_ET(dt):
        # Convert datetime to exchange native time format
        return int(dt.replace(tzinfo=datetime.timezone.utc).timestamp())

    @staticmethod
    def ET_to_seconds(et):
        # Convert exchange native time format to seconds
        return int(et)

    @staticmethod
    def seconds_to_ET(seconds):
        return int(seconds)


_exchange_export = Bybit
