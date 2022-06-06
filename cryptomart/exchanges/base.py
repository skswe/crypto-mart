import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Union

import pandas as pd
from cryptomart.types import TimeType

from ..enums import InstrumentType, Interface, Interval, Symbol
from ..errors import NotSupportedError
from ..feeds import OHLCVFeed

logger = logging.getLogger(__name__)


class ExchangeAPIBase(ABC):
    @property
    @abstractmethod
    def name() -> str:
        pass

    def __init__(self, cache_kwargs: dict = {"disabled": False, "refresh": False}, log_level: str = "INFO"):
        """Init the exchange

        Args:
            cache_kwargs (dict, optional): Cache control settings. See pyutil.cache.cached for details.. Defaults to {"disabled": False, "refresh": False}.
        """
        self.interfaces = {}
        self.logger = logging.getLogger(f"cryptomart.{self.name}")
        self.log_level = log_level
        self.logger.debug(f"Initializing {self.name}")
        self.cache_kwargs = cache_kwargs

    @property
    def log_level(self):
        return self.logger.level

    @log_level.setter
    def log_level(self, level):
        self.logger.setLevel(level)

    def _get_interface(self, interface_name: Interface, inst_type: InstrumentType):
        try:
            interface = self.interfaces[interface_name]
        except KeyError:
            raise NotSupportedError(f"{self.name} does not support {interface_name}")

        if isinstance(interface, dict):
            try:
                interface = interface[inst_type]
            except KeyError:
                raise NotSupportedError(f"{self.name}.{interface_name} does not support {inst_type}")

        return interface

    def _run_interface(self, interface_name: Interface, inst_type: InstrumentType, *args, **kwargs):
        self.logger.debug(f"interface_name={interface_name} | inst_type={inst_type} | args={args} | kwargs={kwargs}")
        return self._get_interface(interface_name, inst_type).run(*args, **kwargs)

    def instrument_info(
        self, inst_type: InstrumentType, map_column: str = None, cache_kwargs: dict = {}
    ) -> Union[pd.DataFrame, Dict[Symbol, Any]]:
        """Get instrument info

        Args:
            inst_type (InstrumentType): Type of instrument to retrieve info for.
            map_column (str): If provided, returns a dict of Symbol -> map_column.
            cache_kwargs (dict): Optional cache control settings. See pyutil.cache.cached for details.
        Returns:
            Union[pd.DataFrame, Dict[Symbol, Any]]: Instrument info
        """
        args = (map_column,)
        return self._run_interface(
            Interface.INSTRUMENT_INFO, inst_type, *args, cache_kwargs=dict(self.cache_kwargs, **cache_kwargs)
        )

    def ohlcv(
        self,
        symbol: Symbol,
        inst_type: InstrumentType,
        interval: Interval = Interval.interval_1d,
        starttime: TimeType = None,
        endtime: TimeType = None,
        strict: bool = False,
        cache_kwargs: dict = {},
    ) -> OHLCVFeed:
        """Get historical OHLCV candlesticks

        Args:
            symbol (Symbol): Symbol to query
            inst_type (InstrumentType): Type of instrument to query
            interval (Interval): Interval or frequency of bars
            starttime (TimeType): Time of the first open
            endtime (TimeType): Time of the last close
            strict (bool): If `True`, raises an exception when missing data is above threshold
            cache_kwargs (dict): Optional cache control settings. See pyutil.cache.cached for details.
        Raises:
            NotSupportedError: If the given symbol, interval are not supported by the API
            MissingDataError: If data does not meet self.valid_data_threshold and `strict=True`.

        Returns:
            OHLCVFeed: OHLCV dataframe with custom methods and properties
        """
        if starttime is None:
            # Get default starttime
            pass
        if endtime is None:
            # Get default endtime
            pass

        args = (symbol, interval, starttime, endtime, strict)
        df = self._run_interface(
            Interface.OHLCV, inst_type, *args, cache_kwargs=dict(self.cache_kwargs, **cache_kwargs)
        )
        return OHLCVFeed(df, self.name, symbol, inst_type, interval, starttime, endtime)

    def order_book(self, symbol: Symbol, inst_type: InstrumentType, depth: int = 20, cache_kwargs: dict = {}):
        """Get orderbook snapshot

        Args:
            symbol (Symbol): Symbol to query
            inst_type (InstrumentType): Type of instrument to query
            depth (int): Number of bids/asks to include in the snapshot
            cache_kwargs (dict): Optional cache control settings. See pyutil.cache.cached for details.

        Returns:
            pd.DataFrame: Orderbook
        """
        args = (symbol, depth)
        return self._run_interface(
            Interface.ORDER_BOOK, inst_type, *args, cache_kwargs=dict(self.cache_kwargs, **cache_kwargs)
        )
