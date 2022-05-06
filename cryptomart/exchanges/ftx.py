import datetime
import logging
import os

import pandas as pd
from cryptomart.feeds import OHLCVColumn
from requests import Request

from ..enums import Interval, OrderBookSchema, OrderBookSide
from .base import ExchangeAPIBase
from .instrument_names.ftx import instrument_names as ftx_instrument_names

logger = logging.getLogger(__name__)


class FTX(ExchangeAPIBase):

    name = "ftx"

    instrument_names = {**ftx_instrument_names}

    intervals = {
        Interval.interval_1m: (60, datetime.timedelta(minutes=1)),
        Interval.interval_5m: (300, datetime.timedelta(minutes=5)),
        Interval.interval_15m: (900, datetime.timedelta(minutes=15)),
        Interval.interval_1h: (3600, datetime.timedelta(hours=1)),
        Interval.interval_1d: (86400, datetime.timedelta(days=1)),
    }

    _base_url = "https://ftx.com/api"
    _max_requests_per_second = 7
    _limit = 1500
    _start_inclusive = True
    _end_inclusive = True
    _ohlcv_column_map = {
        "startTime": OHLCVColumn.open_time,
        "open": OHLCVColumn.open,
        "high": OHLCVColumn.high,
        "low": OHLCVColumn.low,
        "close": OHLCVColumn.close,
        "volume": OHLCVColumn.volume,
    }

    def _ohlcv_prepare_request(self, symbol, instType, interval, starttime, endtime, limit):
        url = f"markets/{symbol}/candles"
        params = {
            "resolution": interval,
            "start_time": starttime,
            "end_time": endtime,
        }
        request_url = os.path.join(self._base_url, url)
        return Request("GET", request_url, params=params)

    def _ohlcv_extract_response(self, response):
        if response["success"] != True:
            # Error has occured

            # Raise general exception for now
            # TODO: build exception handling where reponse error can be fixed
            raise Exception(response["error"])

        return response["result"]

    def _order_book_prepare_request(self, symbol, instType, depth=50):
        request_url = os.path.join(self._base_url, f"markets/{symbol}/orderbook")

        return Request(
            "GET",
            request_url,
            params={
                "depth": depth,
            },
        )

    def _order_book_extract_response(self, response):
        if response["success"] != True:
            # Error has occured

            # Raise general exception for now
            # TODO: build exception handling where reponse error can be fixed
            raise Exception(response["error"])

        response = response["result"]
        bids = pd.DataFrame(response["bids"], columns=[OrderBookSchema.price, OrderBookSchema.quantity]).assign(
            **{OrderBookSchema.side: OrderBookSide.bid}
        )
        asks = pd.DataFrame(response["asks"], columns=[OrderBookSchema.price, OrderBookSchema.quantity]).assign(
            **{OrderBookSchema.side: OrderBookSide.ask}
        )
        return bids.merge(asks, how="outer").assign(
            **{OrderBookSchema.timestamp: datetime.datetime.utcnow().replace(microsecond=0)}
        )

    def _order_book_quantity_multiplier(self, symbol, instType, **kwargs):
        return 1

    @staticmethod
    def ET_to_datetime(et):
        # Convert exchange native time format to datetime
        if isinstance(et, str):
            return datetime.datetime.fromisoformat(et).replace(tzinfo=None)
        else:
            return datetime.datetime.utcfromtimestamp(et)

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


_exchange_export = FTX
