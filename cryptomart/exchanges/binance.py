import datetime
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


class PrepareRequest:
    @staticmethod
    def instrument_info(url: str) -> Request:
        return Request("GET", url)

    @staticmethod
    def ohlcv(
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
    def order_book(url: str, instrument_name: str, depth: int = 20) -> Request:
        return Request(
            "GET",
            url,
            params={
                "symbol": instrument_name,
                "limit": depth,
            },
        )


class ExtractData:
    @staticmethod
    def instrument_info(response: JSONDataType) -> pd.DataFrame:
        data = response["symbols"]

        data = pd.DataFrame(data)
        data = data[data.status == "TRADING"]
        data = data[data.quoteAsset == "USDT"]

        data[Instrument.cryptomart_symbol] = data["baseAsset"]
        data[Instrument.exchange_symbol] = data["symbol"]
        return data

    @staticmethod
    def ohlcv(responses: List[JSONDataType]) -> pd.DataFrame:
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
    def order_book(response: JSONDataType) -> pd.DataFrame:
        if isinstance(response, dict) and "code" in response:
            raise Exception(response["msg"])
        bids = pd.DataFrame(response["bids"], columns=[OrderBookSchema.price, OrderBookSchema.quantity]).assign(
            **{OrderBookSchema.side: OrderBookSide.bid}
        )
        asks = pd.DataFrame(response["asks"], columns=[OrderBookSchema.price, OrderBookSchema.quantity]).assign(
            **{OrderBookSchema.side: OrderBookSide.ask}
        )
        return bids.merge(asks, how="outer").assign(**{OrderBookSchema.timestamp: (response["T"])})


class Binance(ExchangeAPIBase):

    name = "binance"
    interfaces = {}
    futures_base_url = "https://fapi.binance.com"
    spot_base_url = "https://api.binance.com"

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

    def __init__(self):
        super().__init__()
        self.init_dispatchers()
        self.init_instrument_info_interface()
        self.init_instruments()
        self.init_ohlcv_interface()
        self.init_order_book_interface()

    def init_dispatchers(self):
        self.logger.debug("initializing dispatchers")
        self.perpetual_dispatcher = Dispatcher(f"{self.name}.dispatcher.perpetual", timeout=1 / 4)
        self.spot_dispatcher = Dispatcher(f"{self.name}.dispatcher.spot", timeout=1 / 2)

    def init_instruments(self):
        self.logger.debug("initializing instruments")
        self.perpetual_instruments = self.interfaces[Interface.INSTRUMENT_INFO][
            InstrumentType.PERPETUAL
        ].get_symbol_mappings()
        self.spot_instruments = self.interfaces[Interface.INSTRUMENT_INFO][InstrumentType.SPOT].get_symbol_mappings()

    def init_instrument_info_interface(self):
        self.logger.debug("initializing instrument_info interface")
        perpetual = InstrumentInfoInterface(
            prepare_request=PrepareRequest.instrument_info,
            extract_data=ExtractData.instrument_info,
            exchange_name=self.name,
            interface_name=Interface.INSTRUMENT_INFO,
            inst_type=InstrumentType.PERPETUAL,
            url=os.path.join(self.futures_base_url, "fapi/v1/exchangeInfo"),
            dispatcher=self.perpetual_dispatcher,
        )

        spot = InstrumentInfoInterface(
            prepare_request=PrepareRequest.instrument_info,
            extract_data=ExtractData.instrument_info,
            exchange_name=self.name,
            interface_name=Interface.INSTRUMENT_INFO,
            inst_type=InstrumentType.SPOT,
            url=os.path.join(self.spot_base_url, "api/v3/exchangeInfo"),
            dispatcher=self.spot_dispatcher,
        )

        self.interfaces[Interface.INSTRUMENT_INFO] = {
            InstrumentType.PERPETUAL: perpetual,
            InstrumentType.SPOT: spot,
        }

    def init_ohlcv_interface(self):
        self.logger.debug("initializing ohlcv interface")
        perpetual = OHLCVInterface(
            instruments=self.perpetual_instruments,
            intervals=self.intervals,
            time_granularity=datetime.timedelta(milliseconds=1),
            start_inclusive=True,
            end_inclusive=True,
            max_response_limit=1500,
            prepare_request=PrepareRequest.ohlcv,
            extract_data=ExtractData.ohlcv,
            exchange_name=self.name,
            interface_name=Interface.OHLCV,
            inst_type=InstrumentType.PERPETUAL,
            url=os.path.join(self.futures_base_url, "fapi/v1/klines"),
            dispatcher=self.perpetual_dispatcher,
        )

        spot = OHLCVInterface(
            instruments=self.spot_instruments,
            intervals=self.intervals,
            time_granularity=datetime.timedelta(milliseconds=1),
            start_inclusive=True,
            end_inclusive=True,
            max_response_limit=1000,
            prepare_request=PrepareRequest.ohlcv,
            extract_data=ExtractData.ohlcv,
            exchange_name=self.name,
            interface_name=Interface.OHLCV,
            inst_type=InstrumentType.SPOT,
            url=os.path.join(self.spot_base_url, "api/v3/klines"),
            dispatcher=self.spot_dispatcher,
        )

        self.interfaces[Interface.OHLCV] = {
            InstrumentType.PERPETUAL: perpetual,
            InstrumentType.SPOT: spot,
        }

    def init_order_book_interface(self):
        self.logger.debug("initializing order_book interface")
        perpetual = OrderBookInterface(
            prepare_request=PrepareRequest.order_book,
            extract_data=ExtractData.order_book,
            exchange_name=self.name,
            interface_name=Interface.ORDER_BOOK,
            inst_type=InstrumentType.PERPETUAL,
            url=os.path.join(self.futures_base_url, "fapi/v1/depth"),
            dispatcher=self.perpetual_dispatcher,
        )

        spot = OrderBookInterface(
            prepare_request=PrepareRequest.order_book,
            extract_data=ExtractData.order_book,
            exchange_name=self.name,
            interface_name=Interface.ORDER_BOOK,
            inst_type=InstrumentType.SPOT,
            url=os.path.join(self.spot_base_url, "api/v3/depth"),
            dispatcher=self.spot_dispatcher,
        )

        self.interfaces[Interface.ORDER_BOOK] = {
            InstrumentType.PERPETUAL: perpetual,
            InstrumentType.SPOT: spot,
        }

    def _order_book_quantity_multiplier(self, symbol, inst_type, **kwargs):
        return 1


_exchange_export = Binance
