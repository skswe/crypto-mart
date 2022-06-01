import datetime
import logging
import os
from typing import List

import numpy as np
import pandas as pd
from cryptomart.interfaces.instrument_info import InstrumentInfoInterface
from cryptomart.interfaces.order_book import OrderBookInterface
from requests import Request

from ..enums import Instrument, InstrumentType, Interface, Interval, OrderBookSchema, OrderBookSide, Symbol
from ..feeds import OHLCVColumn
from ..interfaces.ohlcv import OHLCVInterface
from ..types import IntervalType, JSONDataType, TimeType
from ..util import Dispatcher
from .base import ExchangeAPIBase

logger = logging.getLogger(__name__)


class Binance(ExchangeAPIBase):

    name = "binance"
    interfaces = {}

    @staticmethod
    def instrument_info_prepare_request(url: str) -> Request:
        return Request("GET", url)

    @staticmethod
    def instrument_info_extract_data(response: JSONDataType) -> pd.DataFrame:
        data = response["symbols"]

        data = pd.DataFrame(data)
        data = data[data.status == "TRADING"]
        data = data[data.quoteAsset == "USDT"]

        data[Instrument.cryptomart_symbol] = data["baseAsset"]
        data[Instrument.exchange_symbol] = data["symbol"]
        return data

    @staticmethod
    def ohlcv_prepare_request(
        url: str,
        instrument_name: str,
        interval: IntervalType,
        starttime: TimeType,
        endtime: TimeType,
        limit: int,
    ) -> Request:
        return Request(
            "GET",
            url,
            params={
                "symbol": instrument_name,
                "interval": interval,
                "startTime": starttime,
                "endTime": endtime,
                "limit": limit,
            },
        )

    @staticmethod
    def ohlcv_extract_data(responses: List[JSONDataType]) -> pd.DataFrame:
        col_map = {
            0: OHLCVColumn.open_time,
            1: OHLCVColumn.open,
            2: OHLCVColumn.high,
            3: OHLCVColumn.low,
            4: OHLCVColumn.close,
            5: OHLCVColumn.volume,
        }

        out = pd.DataFrame(columns=col_map.values())
        for res in responses:
            if isinstance(res, dict) and "code" in res:
                raise Exception(res["msg"])
            data = np.array(data)[:, list(col_map.keys())]
            data = pd.DataFrame(data, columns=list(col_map.values()))
            out = out.append(data, ignore_index=True)

        return out.sort_values(OHLCVColumn.open_time, ascending=True)

    @staticmethod
    def order_book_prepare_request(url: str, instrument_name: str, depth: int = 20) -> Request:
        return Request(
            "GET",
            url,
            params={
                "symbol": instrument_name,
                "limit": depth,
            },
        )

    @staticmethod
    def order_book_extract_data(response: JSONDataType) -> pd.DataFrame:
        if isinstance(response, dict) and "code" in response:
            raise Exception(response["msg"])
        bids = pd.DataFrame(response["bids"], columns=[OrderBookSchema.price, OrderBookSchema.quantity]).assign(
            **{OrderBookSchema.side: OrderBookSide.bid}
        )
        asks = pd.DataFrame(response["asks"], columns=[OrderBookSchema.price, OrderBookSchema.quantity]).assign(
            **{OrderBookSchema.side: OrderBookSide.ask}
        )
        return bids.merge(asks, how="outer").assign(**{OrderBookSchema.timestamp: (response["T"])})

    def __init__(self):
        futures_base_url = "https://fapi.binance.com"
        spot_base_url = "https://api.binance.com"

        perpetual_dispatcher = Dispatcher(f"{self.name}.dispatcher.perpetual", timeout=1 / 4)
        spot_dispatcher = Dispatcher(f"{self.name}.dispatcher.spot", timeout=1 / 2)

        intervals = {
            Interval.interval_1m: ("1m", datetime.timedelta(minutes=1)),
            Interval.interval_5m: ("5m", datetime.timedelta(minutes=5)),
            Interval.interval_15m: ("15m", datetime.timedelta(minutes=15)),
            Interval.interval_1h: ("1h", datetime.timedelta(hours=1)),
            Interval.interval_4h: ("4h", datetime.timedelta(hours=4)),
            Interval.interval_8h: ("8h", datetime.timedelta(hours=8)),
            Interval.interval_12h: ("12h", datetime.timedelta(hours=12)),
            Interval.interval_1d: ("1d", datetime.timedelta(days=1)),
            Interval.interval_1w: ("1w", datetime.timedelta(weeks=1)),
        }

        instrument_info_interface_perpetual = InstrumentInfoInterface(
            prepare_request=self.instrument_info_prepare_request,
            extract_data=self.instrument_info_extract_data,
            exchange_name=self.name,
            interface_name=Interface.INSTRUMENT_INFO,
            inst_type=InstrumentType.PERPETUAL,
            url=os.path.join(futures_base_url, "fapi/v1/exchangeInfo"),
            dispatcher=perpetual_dispatcher,
        )

        instrument_info_interface_spot = InstrumentInfoInterface(
            prepare_request=self.instrument_info_prepare_request,
            extract_data=self.instrument_info_extract_data,
            exchange_name=self.name,
            interface_name=Interface.INSTRUMENT_INFO,
            inst_type=InstrumentType.PERPETUAL,
            url=os.path.join(spot_base_url, "api/v3/exchangeInfo"),
            dispatcher=spot_dispatcher,
        )

        perpetual_instruments = instrument_info_interface_perpetual.get_symbol_mappings()
        spot_instruments = instrument_info_interface_spot.get_symbol_mappings()

        ohlcv_interface_perpetual = OHLCVInterface(
            instruments=perpetual_instruments,
            intervals=intervals,
            time_granularity=datetime.timedelta(milliseconds=1),
            start_inclusive=True,
            end_inclusive=True,
            max_response_limit=1500,
            prepare_request=self.ohlcv_prepare_request,
            extract_data=self.ohlcv_extract_data,
            exchange_name=self.name,
            interface_name=Interface.OHLCV,
            inst_type=InstrumentType.PERPETUAL,
            url=os.path.join(futures_base_url, "fapi/v1/klines"),
            dispatcher=perpetual_dispatcher,
        )

        ohlcv_interface_spot = OHLCVInterface(
            instruments=spot_instruments,
            intervals=intervals,
            time_granularity=datetime.timedelta(milliseconds=1),
            start_inclusive=True,
            end_inclusive=True,
            max_response_limit=1000,
            prepare_request=self.ohlcv_prepare_request,
            extract_data=self.ohlcv_extract_data,
            exchange_name=self.name,
            interface_name=Interface.OHLCV,
            inst_type=InstrumentType.SPOT,
            url=os.path.join(spot_base_url, "api/v3/klines"),
            dispatcher=spot_dispatcher,
        )

        order_book_interface_perpetual = OrderBookInterface(
            prepare_request=self.order_book_prepare_request,
            extract_data=self.order_book_extract_data,
            exchange_name=self.name,
            interface_name=Interface.ORDER_BOOK,
            inst_type=InstrumentType.PERPETUAL,
            url=os.path.join(futures_base_url, "fapi/v1/depth"),
            dispatcher=perpetual_dispatcher,
        )

        order_book_interface_spot = OrderBookInterface(
            prepare_request=self.order_book_prepare_request,
            extract_data=self.order_book_extract_data,
            exchange_name=self.name,
            interface_name=Interface.ORDER_BOOK,
            inst_type=InstrumentType.SPOT,
            url=os.path.join(spot_base_url, "api/v3/depth"),
            dispatcher=spot_dispatcher,
        )

        self.interfaces = {
            Interface.INSTRUMENT_INFO: {
                InstrumentType.PERPETUAL: instrument_info_interface_perpetual,
                InstrumentType.SPOT: instrument_info_interface_spot,
            },
            Interface.OHLCV: {
                InstrumentType.PERPETUAL: ohlcv_interface_perpetual,
                InstrumentType.SPOT: ohlcv_interface_spot,
            },
            Interface.ORDER_BOOK: {
                InstrumentType.PERPETUAL: order_book_interface_perpetual,
                InstrumentType.SPOT: order_book_interface_spot,
            },
        }

    def _order_book_quantity_multiplier(self, symbol, inst_type, **kwargs):
        return 1


_exchange_export = Binance
