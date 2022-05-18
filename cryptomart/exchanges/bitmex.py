import datetime
import logging
import os
from typing import Dict, List, Union

import numpy as np
import pandas as pd
from requests import Request

from ..enums import FundingRateSchema, Interval, OrderBookSchema, OrderBookSide
from ..feeds import OHLCVColumn
from .base import ExchangeAPIBase
from .instrument_names.bitmex import instrument_names as bitmex_instrument_names

logger = logging.getLogger(__name__)


class BitMEX(ExchangeAPIBase):

    name = "bitmex"

    instrument_names = {**bitmex_instrument_names}

    intervals = {
        Interval.interval_1m: ("1m", datetime.timedelta(minutes=1)),
        Interval.interval_5m: ("5m", datetime.timedelta(minutes=5)),
        Interval.interval_1h: ("1h", datetime.timedelta(hours=1)),
        Interval.interval_1d: ("1d", datetime.timedelta(days=1)),
    }

    _base_url = "https://www.bitmex.com/api/v1"
    _max_requests_per_second = 0.5
    _ohlcv_limit = 1000
    _funding_rate_limit = 1000
    _start_inclusive = True
    _end_inclusive = True
    _tolerance = "8h"
    _ohlcv_column_map = {
        "timestamp": OHLCVColumn.open_time,
        "open": OHLCVColumn.open,
        "high": OHLCVColumn.high,
        "low": OHLCVColumn.low,
        "close": OHLCVColumn.close,
        "volume": OHLCVColumn.volume,
    }
    _funding_rate_column_map = {
        "timestamp": FundingRateSchema.timestamp,
        "fundingRate": FundingRateSchema.funding_rate,
    }

    def _ohlcv_prepare_request(self, symbol, instType, interval, starttime, endtime, limit):
        url = "trade/bucketed"
        params = {
            "symbol": symbol,
            "binSize": interval,
            "count": limit,
            "startTime": datetime.datetime.fromtimestamp(int(starttime / 1000)),
            "endTime": datetime.datetime.fromtimestamp(int(endtime / 1000)),
            "columns": ["open", "high", "low", "close", "volume"],
        }
        request_url = os.path.join(self._base_url, url)
        return Request("GET", request_url, params=params)

    def _ohlcv_extract_response(self, response):
        if isinstance(response, dict):
            # Error has occured

            # Raise general exception for now
            # TODO: build exception handling where reponse error can be fixed
            raise Exception(response["error"]["message"])
        return response

    def _order_book_prepare_request(self, symbol, instType, depth=50):
        request_url = os.path.join(self._base_url, "orderBook/L2")

        return Request(
            "GET",
            request_url,
            params={
                "symbol": symbol,
                "depth": depth,
            },
        )

    def _order_book_extract_response(self, response):
        if isinstance(response, dict):
            # Error has occured

            # Raise general exception for now
            # TODO: build exception handling where reponse error can be fixed
            raise Exception(response["error"]["message"])
        df = (
            pd.DataFrame(response)
            .drop(columns=["symbol", "id"])
            .reindex(columns=[OrderBookSchema.price, "size", OrderBookSchema.side])
            .rename(columns={"size": OrderBookSchema.quantity})
            .replace(["Sell", "Buy"], [OrderBookSide.ask, OrderBookSide.bid])
            .assign(**{OrderBookSchema.timestamp: datetime.datetime.now().replace(microsecond=0)})
        )
        return df

    def _order_book_quantity_multiplier(self, symbol, instType, **kwargs):
        return 1

    def _funding_rate_prepare_request(self, symbol, instType, starttime, endtime, limit):
        request_url = os.path.join(self._base_url, "funding")
        
        params = {
            "symbol": symbol,
            "startTime": self.ET_to_datetime(starttime),
            "endTime": self.ET_to_datetime(endtime),
            "count": limit,
        }

        return Request(
            "GET",
            request_url,
            params=params,
        )

    def _funding_rate_extract_response(self, response):
        if isinstance(response, list) and "code" in response:
            # Error has occured

            # Raise general exception for now
            # TODO: build exception handling where reponse error can be fixed
            raise Exception(response["msg"])
        return response

    @staticmethod
    def ET_to_datetime(et):
        # Convert exchange native time format to datetime
        if isinstance(et, str):
            return datetime.datetime.fromisoformat(et[:-1]).replace(tzinfo=None)
        else:
            return datetime.datetime.utcfromtimestamp(int(et) / 1000)

    @staticmethod
    def datetime_to_ET(dt):
        # Convert datetime to exchange native time format
        return int(dt.replace(tzinfo=datetime.timezone.utc).timestamp() * 1000)

    @staticmethod
    def ET_to_seconds(et):
        # Convert exchange native time format to seconds
        return int(int(et) / 1000)

    @staticmethod
    def seconds_to_ET(seconds):
        return int(seconds * 1000)

    # BitMEX returns timestamp as close_time instead ofopen_time like other exchanges
    def _ohlcv_res_to_dataframe(
        self,
        data: List[Union[dict, list]],
        starttime: datetime.datetime,
        endtime: datetime.datetime,
        timedelta: datetime.timedelta,
        time_column: str = "open_time",
    ):
        return super()._ohlcv_res_to_dataframe(data, starttime, endtime, timedelta, "close_time")


_exchange_export = BitMEX
