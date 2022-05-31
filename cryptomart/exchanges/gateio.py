import datetime
import logging
import os

import pandas as pd
from pyutil.cache import cached
from requests import Request, get

from ..enums import InstrumentType, Interval, OrderBookSchema, OrderBookSide
from ..feeds import OHLCVColumn
from .base import ExchangeAPIBase
from .instrument_names.gateio import instrument_names as gateio_instrument_names

logger = logging.getLogger(__name__)


class GateIO(ExchangeAPIBase):
    name = "gateio"

    instrument_names = {**gateio_instrument_names}

    intervals = {
        Interval.interval_1m: ("1m", datetime.timedelta(minutes=1)),
        Interval.interval_5m: ("5m", datetime.timedelta(minutes=5)),
        Interval.interval_15m: ("15m", datetime.timedelta(minutes=15)),
        Interval.interval_30m: ("30m", datetime.timedelta(minutes=30)),
        Interval.interval_1h: ("1h", datetime.timedelta(hours=1)),
        Interval.interval_4h: ("4h", datetime.timedelta(hours=4)),
        Interval.interval_8h: ("8h", datetime.timedelta(hours=8)),
        Interval.interval_1d: ("1d", datetime.timedelta(days=1)),
    }

    _base_url = "https://api.gateio.ws/api/v4"
    _max_requests_per_second = 100
    _limit = 200
    _start_inclusive = True
    _end_inclusive = True
    _ohlcv_column_map = {
        "t": OHLCVColumn.open_time,
        "o": OHLCVColumn.open,
        "h": OHLCVColumn.high,
        "l": OHLCVColumn.low,
        "c": OHLCVColumn.close,
        "v": OHLCVColumn.volume,
    }

    _ohlcv_column_map_spot = {
        0: OHLCVColumn.open_time,
        5: OHLCVColumn.open,
        3: OHLCVColumn.high,
        4: OHLCVColumn.low,
        2: OHLCVColumn.close,
        1: OHLCVColumn.volume,
    }

    def _ohlcv_prepare_request(self, symbol, inst_type, interval, starttime, endtime, limit):
        url = "spot/candlesticks" if inst_type == InstrumentType.SPOT else "futures/usdt/candlesticks"

        params = {
            "contract": symbol,
            "interval": interval,
            "from": starttime,
            "to": endtime,
        }

        request_url = os.path.join(self._base_url, url)
        return Request("GET", request_url, params=params)

    def _ohlcv_extract_response(self, response):
        if isinstance(response, dict):
            # Error has occured

            # Raise general exception for now
            # TODO: build exception handling where reponse error can be fixed
            raise Exception(response["label"])

        return response[:-1]

    def _order_book_prepare_request(self, symbol, inst_type, depth=50):
        request_url = os.path.join(self._base_url, "futures/usdt/order_book")

        return Request(
            "GET",
            request_url,
            params={
                "contract": symbol,
                "limit": depth,
            },
        )

    def _order_book_extract_response(self, response):
        if isinstance(response, dict) and "asks" not in response:
            # Error has occured

            # Raise general exception for now
            # TODO: build exception handling where reponse error can be fixed
            raise Exception(response["label"])

        bids = pd.DataFrame(response["bids"]).assign(**{OrderBookSchema.side: OrderBookSide.bid})
        asks = pd.DataFrame(response["asks"]).assign(**{OrderBookSchema.side: OrderBookSide.ask})
        df = (
            bids.merge(asks, how="outer")
            .assign(
                **{
                    OrderBookSchema.timestamp: pd.to_datetime(response["current"] * 1e9)
                    .replace(nanosecond=0)
                    .replace(microsecond=0)
                }
            )
            .rename(columns={"p": OrderBookSchema.price, "s": OrderBookSchema.quantity})
            .reindex(columns=OrderBookSchema._names())
        )

        return df

    @cached("/tmp/cache/order_book_multiplier", is_method=True, instance_identifiers=["name"], log_level="DEBUG")
    def _order_book_quantity_multiplier(self, symbol, inst_type, **kwargs):
        request_url = os.path.join(self._base_url, f"futures/usdt/contracts/{symbol}")
        logger.debug(request_url)
        res = get(request_url).json()
        return float(res["quanto_multiplier"])

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


_exchange_export = GateIO
