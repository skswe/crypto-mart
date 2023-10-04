"""Main API"""

import importlib
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Union

import pandas as pd

from .enums import Exchange, InstrumentType, Interval
from .exchanges import Binance, BitMEX, Bybit, GateIO, Kucoin, OKEx
from .exchanges.base import ExchangeAPIBase
from .feeds import FundingRateFeed, OHLCVFeed
from .globals import LOGGING_FORMATTER
from .types import TimeType

logger = logging.getLogger(__name__)


class Client:
    """Unified interface to all registered Exchanges"""

    def __init__(
        self,
        exchanges: List[Exchange] = Exchange._names(),
        cache_kwargs: dict = {"disabled": False, "refresh": False},
        log_level: str = "INFO",
        log_file: str = None,
        quiet: bool = False,
        instrument_cache_kwargs: dict = {"disabled": False, "refresh": False},
        **kwargs,
    ):
        """Unified interface to all registered Exchanges.

        Args:
            exchanges (List[Exchange], optional): Exchanges to include in the DataMart. Defaults to Exchange._names().
            debug (bool, optional): [description]. Defaults to False.
            log_file (str, optional): file to save logs to. Defaults to None.
            exchange_init_kwargs: kwargs to pass to creation of each exchange object in `exchanges`
            quiet: If True, hides initialization logs.
        """
        if quiet:
            # Disables all logs at INFO or below
            logging.disable(logging.INFO)

        logger.info("=" * 80)
        logger.info("Initializing client... (To hide initialization logs, pass quiet=True)")
        self._cache_kwargs = cache_kwargs
        logging.getLogger("cryptomart").setLevel(log_level)

        if log_file is not None:
            if os.path.exists(log_file):
                logger.info(f"Removing old log file: {log_file}")
                os.remove(log_file)
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            handler = logging.FileHandler(log_file)
            handler.setFormatter(LOGGING_FORMATTER)
            logging.getLogger().addHandler(handler)

        for exchange in exchanges:
            assert exchange in Exchange._names(), f"{exchange} is not registered as an Exchange"

        self._active_exchanges = [getattr(Exchange, e) for e in exchanges]
        self._exchange_instance_map: Dict[Exchange, ExchangeAPIBase] = {}
        self._exchange_class_map = {}
        self._load_exchanges(
            cache_kwargs=cache_kwargs, log_level=log_level, instrument_cache_kwargs=instrument_cache_kwargs
        )
        logger.info("Client initialized")
        logger.info("=" * 80)

        if quiet:
            # Enable all logs
            logging.disable(logging.NOTSET)

    def instrument_info(
        self, exchange: Exchange, inst_type: InstrumentType, map_column: str = None, cache_kwargs: dict = {}
    ) -> Union[pd.DataFrame, Dict[str, Any]]:
        """Get instrument info

        Args:
            exchange (Exchange): Registered exchange to call
            inst_type (InstrumentType): Type of instrument to retrieve info for.
            map_column (str): If provided, returns a dict of symbol -> map_column.
            cache_kwargs (dict): Optional cache control settings.
        Returns:
            Union[pd.DataFrame, Dict[str, Any]]: Instrument info
        """
        return self._exchange_instance_map[exchange].instrument_info(
            inst_type, map_column=map_column, cache_kwargs=cache_kwargs
        )

    def ohlcv(
        self,
        exchange: Exchange,
        symbol: str,
        inst_type: InstrumentType,
        starttime: TimeType,
        endtime: TimeType,
        interval: Interval = Interval.interval_1d,
        strict: bool = False,
        cache_kwargs: dict = {},
    ) -> OHLCVFeed:
        """Get historical OHLCV candlesticks

        Args:
            exchange (Exchange): Registered exchange to call
            symbol (str): Symbol to query
            inst_type (InstrumentType): Type of instrument to query
            interval (Interval): Interval or frequency of bars
            starttime (TimeType): Time of the first open
            endtime (TimeType): Time of the last close
            strict (bool): If `True`, raises an exception when missing data is above threshold
            cache_kwargs (dict): Optional cache control settings.
        Raises:
            NotSupportedError: If the given symbol, interval are not supported by the API
            MissingDataError: If data does not meet self.valid_data_threshold and `strict=True`.

        Returns:
            OHLCVFeed: OHLCV dataframe with custom methods and properties
        """
        return self._exchange_instance_map[exchange].ohlcv(
            symbol,
            inst_type,
            starttime=starttime,
            endtime=endtime,
            interval=interval,
            strict=strict,
            cache_kwargs=cache_kwargs,
        )

    def funding_rate(
        self,
        exchange: Exchange,
        symbol: str,
        starttime: TimeType,
        endtime: TimeType,
        strict: bool = False,
        cache_kwargs: dict = {},
    ) -> FundingRateFeed:
        """Run main interface function

        Args:
            exchange (Exchange): Registered exchange to call
            symbol (str): Symbol to query
            starttime (TimeType): Time of the first open
            endtime (TimeType): Time of the last close
            strict (bool): If `True`, raises an exception when missing data is above threshold
        Raises:
            NotSupportedError: If the given symbol is not supported by the API
            MissingDataError: If data does not meet self.valid_data_threshold and `strict=True`.

        Returns:
            pd.DataFrame: funding rate dataframe
        """
        return self._exchange_instance_map[exchange].funding_rate(
            symbol, starttime=starttime, endtime=endtime, strict=strict, cache_kwargs=cache_kwargs
        )

    def order_book(
        self, exchange: Exchange, symbol: str, inst_type: InstrumentType, depth: int = 20, cache_kwargs: dict = {}
    ):
        """Get orderbook snapshot

        Args:
            exchange (Exchange): Registered exchange to call
            symbol (str): Symbol to query
            inst_type (InstrumentType): Type of instrument to query
            depth (int): Number of bids/asks to include in the snapshot
            cache_kwargs (dict): Optional cache control settings.

        Returns:
            pd.DataFrame: Orderbook
        """
        return self._exchange_instance_map[exchange].order_book(
            symbol, inst_type, depth=depth, cache_kwargs=cache_kwargs
        )

    @property
    def binance(self) -> Binance:
        return self._exchange_instance_map[Exchange.BINANCE]

    @property
    def bitmex(self) -> BitMEX:
        return self._exchange_instance_map[Exchange.BITMEX]

    @property
    def bybit(self) -> Bybit:
        return self._exchange_instance_map[Exchange.BYBIT]

    @property
    def okex(self) -> OKEx:
        return self._exchange_instance_map[Exchange.OKEX]

    @property
    def gateio(self) -> GateIO:
        return self._exchange_instance_map[Exchange.GATEIO]

    @property
    def kucoin(self) -> Kucoin:
        return self._exchange_instance_map[Exchange.KUCOIN]

    def _load_exchanges(self, **kwargs):
        # Import exchange classes
        for exchange in self._active_exchanges:
            exchange_module = importlib.import_module(f".exchanges.{exchange}", __package__)
            self._exchange_class_map[exchange] = exchange_module._exchange_export

        def _init_exchange_thread(exchange_name: str, exchange_cls: ExchangeAPIBase, exchange_kwargs: dict):
            self._exchange_instance_map[exchange_name] = exchange_cls(**exchange_kwargs)

        # Map each instantiation to its own thread to minimize http request blocking
        with ThreadPoolExecutor(max_workers=len(self._active_exchanges)) as executor:
            errors = executor.map(
                _init_exchange_thread,
                self._exchange_class_map.keys(),
                self._exchange_class_map.values(),
                [kwargs] * len(self._exchange_class_map),
            )

        for error in errors:
            if error:
                logger.error(f"Error returned while initializing exchange: {error}")

    @property
    def log_level(self):
        return logging.getLogger("cryptomart").level

    @log_level.setter
    def log_level(self, level):
        logging.getLogger("cryptomart").setLevel(level)
        for exch in self._exchange_instance_map.values():
            exch.log_level = level

    @property
    def cache_kwargs(self):
        return self._cache_kwargs

    @cache_kwargs.setter
    def cache_kwargs(self, cache_kwargs):
        self._cache_kwargs = cache_kwargs
        for exch in self._exchange_instance_map.values():
            exch.cache_kwargs = cache_kwargs

    @property
    def exchanges(self):
        return [exchange_instance for exchange_enum, exchange_instance in self._exchange_instance_map.items()]
