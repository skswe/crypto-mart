"""Main API"""

import importlib
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List

from .enums import Exchange
from .exchanges import FTX, Binance, BitMEX, Bybit, CoinFLEX, GateIO, Kucoin, OKEx
from .exchanges.base import ExchangeAPIBase
from .globals import LOGGING_FORMATTER

logger = logging.getLogger(__name__)


class Client:
    """Unified interface to all registered Exchanges"""

    def __init__(
        self,
        exchanges: List[Exchange] = Exchange._names(),
        log_level="INFO",
        log_file=None,
        exchange_init_kwargs={},
        **kwargs,
    ):
        """Unified interface to all registered Exchanges.

        Args:
            exchanges (List[Exchange], optional): Exchanges to include in the DataMart. Defaults to Exchange._names().
            debug (bool, optional): [description]. Defaults to False.
            log_file (str, optional): file to save logs to. Defaults to None.
            exchange_init_kwargs: kwargs to pass to creation of each exchange object in `exchanges`
        """
        self.log_level = log_level

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
        self._exchange_instance_map = {}
        self._exchange_class_map = {}
        self._load_exchanges(**exchange_init_kwargs)

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
    def coinflex(self) -> CoinFLEX:
        return self._exchange_instance_map[Exchange.COINFLEX]

    @property
    def ftx(self) -> FTX:
        return self._exchange_instance_map[Exchange.FTX]

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

        # Map each instantiation to its own thread to minimuze http request blocking
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
        logging.getLogger("pyutil").setLevel(level)

    @property
    def exchanges(self):
        return [exchange_instance for exchange_enum, exchange_instance in self._exchange_instance_map.items()]
