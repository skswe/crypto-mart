import datetime
import logging
import os
from queue import PriorityQueue

import pandas as pd
import requests
from cryptomart.feeds import OHLCVColumn
from pyutil.cache import cached
from requests import Request

from ..enums import FundingRateSchema, InstrumentType, Interval, OrderBookSchema, OrderBookSide
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

    _base_url = "https://api.bybit.com"
    _max_requests_per_second = 40
    _ohlcv_limit = 200
    _funding_rate_limit = 200
    _tolerance = "8h"
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
    _funding_rate_column_map = {
        "time": FundingRateSchema.timestamp,
        "value": FundingRateSchema.funding_rate,
    }

    def _ohlcv_prepare_request(self, symbol, instType, interval, starttime, endtime, limit):
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

    def _order_book_prepare_request(self, symbol, instType, depth):
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

    def _order_book_quantity_multiplier(self, symbol, instType, **kwargs):
        return 1

    def _funding_rate_prepare_request(self, symbol, instType, starttime, endtime, limit):
        request_url = os.path.join(self._base_url, "v2/public/funding/prev-funding-rate")

        return Request(
            "GET",
            request_url,
            params={
                "symbol": symbol,
            },
        )

    def _funding_rate_extract_response(self, response):
        if response["ret_msg"] != "OK":
            # Error has occured

            # Raise general exception for now
            # TODO: build exception handling where reponse error can be fixed
            raise Exception(response["error"])
        return response

    @staticmethod
    def ET_to_datetime(et):
        # Convert exchange native time format to datetime
        if isinstance(et, str):
            return datetime.datetime.strptime(et, "%Y-%m-%d %H:%M:%S")

        else:
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

    @cached("/tmp/cache/historical_funding_rate", is_method=True, instance_identifiers=["name"])
    def _funding_rate(
        self,
        symbol_name: str,
        instType: InstrumentType,
        starttime: datetime.datetime,
        endtime: datetime.datetime,
        timedelta: datetime.timedelta,
        cache_kwargs={},
    ) -> pd.DataFrame:
        """Return historical funding rates for given instrument"""
        if callable(self._funding_rate_limit):
            limit = self._funding_rate_limit(timedelta)
        else:
            limit = self._funding_rate_limit or 100

        data = []
        # api_timedelta is the effective timedelta (interval) of the funding rate data provided by the api
        api_timedelta = self._funding_rate_interval

        start_times, end_times, limits = self._ohlcv_get_request_intervals(starttime, endtime, api_timedelta, limit)
        for _starttime, _endtime, limit in zip(start_times, end_times, limits):

            i = 1
            last_page = 1
            while i <= last_page:
                date = (
                    str(datetime.datetime.date(self.ET_to_datetime(_starttime)))
                    + "~"
                    + str(datetime.datetime.date(self.ET_to_datetime(_endtime)))
                )

                _params = {"symbol": symbol_name, "date": date, "page": i}
                _res = requests.get("https://api2.bybit.com/linear/funding-rate/list", params=_params).json()
                last_page = _res["result"]["last_page"]
                page_data = _res["result"]["data"]
                data.extend(page_data)
                i += 1

        data: pd.DataFrame = pd.DataFrame(data).loc[:, self._funding_rate_column_map.keys()]
        data.rename(columns=self._funding_rate_column_map, inplace=True)

        df_funding = self._funding_rate_res_to_dataframe(data, starttime, endtime, timedelta)

        return df_funding


_exchange_export = Bybit
