import datetime
import logging
import os

import pandas as pd
from requests import Request

from ..enums import InstrumentType, Interval, OrderBookSchema, OrderBookSide
from ..feeds import OHLCVColumn
from .base import ExchangeAPIBase
from .instrument_names.binance import instrument_names as binance_instrument_names

logger = logging.getLogger(__name__)


class Binance(ExchangeAPIBase):

    name = "binance"

    instrument_names = {**binance_instrument_names}

    intervals = {
        Interval.interval_1m: ("1m", datetime.timedelta(minutes=1)),
        Interval.interval_3m: ("3m", datetime.timedelta(minutes=3)),
        Interval.interval_5m: ("5m", datetime.timedelta(minutes=5)),
        Interval.interval_15m: ("15m", datetime.timedelta(minutes=15)),
        Interval.interval_30m: ("30m", datetime.timedelta(minutes=30)),
        Interval.interval_1h: ("1h", datetime.timedelta(hours=1)),
        Interval.interval_2h: ("2h", datetime.timedelta(hours=2)),
        Interval.interval_4h: ("4h", datetime.timedelta(hours=4)),
        Interval.interval_6h: ("6h", datetime.timedelta(hours=6)),
        Interval.interval_8h: ("8h", datetime.timedelta(hours=8)),
        Interval.interval_12h: ("12h", datetime.timedelta(hours=12)),
        Interval.interval_1d: ("1d", datetime.timedelta(days=1)),
    }

    @property
    def fee_pct(self):
        return 0.0004

    _base_url = "https://fapi.binance.com/fapi/v1"
    _max_requests_per_second = 4
    _limit = 1500
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

    def _ohlcv_prepare_request(self, instType, symbol, interval, starttime, endtime, limit):
        if instType == InstrumentType.PERPETUAL:
            url = "klines"
            params = {
                "symbol": symbol,
                "interval": interval,
                "startTime": starttime,
                "endTime": endtime,
                "limit": limit,
            }
        elif instType == InstrumentType.QUARTERLY:
            url = "continuousKlines"
            params = {
                "pair": symbol,
                "contractType": "CURRENT_QUARTER",
                "interval": interval,
                "startTime": starttime,
                "endTime": endtime,
                "limit": limit,
            }

        request_url = os.path.join(self._base_url, url)
        return Request("GET", request_url, params=params)

    def _ohlcv_extract_response(self, response):
        if isinstance(response, dict) and "code" in response:
            # Error has occured

            # Raise general exception for now
            # TODO: build exception handling where reponse error can be fixed
            raise Exception(response["msg"])
        return response

    def _order_book_prepare_request(self, instType, symbol, depth=50):
        request_url = os.path.join(self._base_url, "depth")

        return Request(
            "GET",
            request_url,
            params={
                "symbol": symbol,
                "limit": depth,
            },
        )

    def _order_book_extract_response(self, response):
        if isinstance(response, dict) and "code" in response:
            # Error has occured

            # Raise general exception for now
            # TODO: build exception handling where reponse error can be fixed
            raise Exception(response["msg"])
        bids = pd.DataFrame(response["bids"], columns=[OrderBookSchema.price, OrderBookSchema.quantity]).assign(
            **{OrderBookSchema.side: OrderBookSide.bid}
        )
        asks = pd.DataFrame(response["asks"], columns=[OrderBookSchema.price, OrderBookSchema.quantity]).assign(
            **{OrderBookSchema.side: OrderBookSide.ask}
        )
        return bids.merge(asks, how="outer").assign(
            **{OrderBookSchema.timestamp: self.ET_to_datetime(response["T"]).replace(microsecond=0)}
        )

    def _order_book_quantity_multiplier(self, instType, symbol, **kwargs):
        return 1


_exchange_export = Binance
