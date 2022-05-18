import datetime
import logging
import os

import pandas as pd
from requests import Request

from ..enums import FundingRateSchema, Interval, OrderBookSchema, OrderBookSide
from ..feeds import OHLCVColumn
from .base import ExchangeAPIBase
from .instrument_names.coinflex import instrument_names as coinflex_instrument_names

logger = logging.getLogger(__name__)


class CoinFLEX(ExchangeAPIBase):

    name = "coinflex"

    instrument_names = {**coinflex_instrument_names}

    intervals = {
        Interval.interval_1m: ("60s", datetime.timedelta(minutes=1)),
        Interval.interval_5m: ("300s", datetime.timedelta(minutes=5)),
        Interval.interval_15m: ("900s", datetime.timedelta(minutes=15)),
        Interval.interval_30m: ("1800s", datetime.timedelta(minutes=30)),
        Interval.interval_1h: ("3600s", datetime.timedelta(hours=1)),
        Interval.interval_2h: ("7200s", datetime.timedelta(hours=2)),
        Interval.interval_4h: ("14400s", datetime.timedelta(hours=4)),
        Interval.interval_1d: ("86400s", datetime.timedelta(days=1)),
    }

    _base_url = "https://v2api.coinflex.com"
    _max_requests_per_second = 20
    _start_inclusive = True
    _end_inclusive = True
    _tolerance = datetime.timedelta(hours=1)
    _ohlcv_column_map = {
        "openedAt": OHLCVColumn.open_time,
        "open": OHLCVColumn.open,
        "high": OHLCVColumn.high,
        "low": OHLCVColumn.low,
        "close": OHLCVColumn.close,
        "volume": OHLCVColumn.volume,
    }
    _funding_rate_column_map = {
        "createdAt": FundingRateSchema.timestamp,
        "fundingRate": FundingRateSchema.funding_rate,
    }

    def _funding_rate_limit(self, interval: datetime.timedelta) -> int:
        """Returns exchange's funding rate record limit given interval of requsted records"""

        TIME_LIMIT = datetime.timedelta(days=7)
        RECORD_LIMIT = 500
        return min(RECORD_LIMIT, int(TIME_LIMIT / interval))

    def _ohlcv_limit(self, interval: datetime.timedelta) -> int:
        """Returns exchange's funding rate record limit given interval of requsted records"""

        TIME_LIMIT = datetime.timedelta(days=7)
        RECORD_LIMIT = 5000
        return min(RECORD_LIMIT, int(TIME_LIMIT / interval))

    def _ohlcv_prepare_request(self, symbol, instType, interval, starttime, endtime, limit):
        url = f"v3/candles"
        params = {
            "marketCode": symbol,
            "timeframe": interval,
            "limit": limit,
            "startTime": starttime,
            "endTime": endtime,
        }
        request_url = os.path.join(self._base_url, url)
        return Request("GET", request_url, params=params)

    def _ohlcv_extract_response(self, response):
        if "error" in response:
            # TODO: build exception handling where reponse error can be fixed
            raise Exception(response["message"])
        else:
            return response["data"]

    def _order_book_prepare_request(self, symbol, instType, depth=50):
        request_url = os.path.join(self._base_url, f"v2/depth/{symbol}/{depth}")

        return Request("GET", request_url)

    def _order_book_extract_response(self, response):
        if len(response["data"]) == 0:
            # Error has occured

            # Raise general exception for now
            # TODO: build exception handling where reponse error can be fixed
            raise Exception("No data found for these parameters")
        response = response["data"][0]
        bids = pd.DataFrame(response["bids"], columns=[OrderBookSchema.price, OrderBookSchema.quantity]).assign(
            **{OrderBookSchema.side: OrderBookSide.bid}
        )
        asks = pd.DataFrame(response["asks"], columns=[OrderBookSchema.price, OrderBookSchema.quantity]).assign(
            **{OrderBookSchema.side: OrderBookSide.ask}
        )
        return bids.merge(asks, how="outer").assign(
            **{OrderBookSchema.timestamp: self.ET_to_datetime(response["timestamp"]).replace(microsecond=0)}
        )

    def _order_book_quantity_multiplier(self, symbol, instType, **kwargs):
        return 1

    def _funding_rate_prepare_request(self, symbol, instType, starttime, endtime, limit):
        request_url = os.path.join(self._base_url, "v3/funding-rates")

        params = {
            "marketCode": symbol,
            "startTime": starttime,
            "endTime": endtime,
            # "limit": limit,
        }

        return Request(
            "GET",
            request_url,
            params=params,
        )

    def _funding_rate_extract_response(self, response):
        if not response["success"]:
            # TODO: build exception handling where reponse error can be fixed
            raise Exception(response["message"])
        else:
            return response["data"]

_exchange_export = CoinFLEX
