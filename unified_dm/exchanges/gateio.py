import datetime
import logging
import os

import pandas as pd
from requests import Request, get

from ..enums import Interval, OrderBookSchema, OrderBookSide,FundingRateSchema
from ..feeds import OHLCVColumn
from ..util import cached
from .bases import ExchangeAPIBase
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

    @property
    def fee_pct(self):
        return 0.00075

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
    _funding_rate_column_map = {
        "t": FundingRateSchema.timestamp,
        "r": FundingRateSchema.funding_rate 
    }

    def _ohlcv_prepare_request(self, instType, symbol, interval, starttime, endtime, limit):
        url = "futures/usdt/candlesticks"
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

    def _order_book_prepare_request(self, instType, symbol, depth=50):
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
            .reindex(columns=OrderBookSchema.names())
        )

        return df

    @cached("cache/order_book_multiplier", is_method=True, instance_identifier="name", log_level="DEBUG")
    def _order_book_quantity_multiplier(self, instType, symbol):
        request_url = os.path.join(self._base_url, f"futures/usdt/contracts/{symbol}")
        logger.debug(request_url)
        res = get(request_url).json()
        return float(res["quanto_multiplier"])

    def _histrorical_funding_rate_prepare_request(self, instType, symbol, starttime, endtime, limit):
        url = "futures/usdt/funding_rate?contract"
        params = {
            "contract": symbol,
        }
        request_url = os.path.join(self._base_url,url)
        print(request_url)
        return Request(
                "GET",
                request_url,
                params= params,
        )
    
    def _histrorical_funding_rate_extract_response(self, response):
        if isinstance(response, list) and "code" in response:
            # Error has occured

            # Raise general exception for now
            # TODO: build exception handling where reponse error can be fixed
            raise Exception(response["msg"])
        return response
    
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
