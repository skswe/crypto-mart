"""Main API"""

import importlib
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List

from .enums import Exchange
from .exchanges.base import ExchangeAPIBase
from .globals import LOGGING_FORMATTER

logger = logging.getLogger(__name__)


class Client:
    """Unified interface to all registered Exchanges"""

    def __init__(
        self,
        exchanges: List[Exchange] = Exchange._names(),
        debug=False,
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
        if debug:
            self.log_level = logging.DEBUG
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
        self._load_exchanges(debug=debug, **exchange_init_kwargs)

    def _load_exchanges(self, **kwargs):
        # Import exchange classes
        for exchange in self._active_exchanges:
            exchange_module = importlib.import_module(f".exchanges.{exchange}", __package__)
            self._exchange_class_map[exchange] = exchange_module._exchange_export

        def _init_exchange_thread(exchange_name: str, exchange_cls: ExchangeAPIBase, exchange_kwargs: dict):
            inst = exchange_cls(**exchange_kwargs)
            setattr(self, exchange_name, inst)
            self._exchange_instance_map[exchange_name] = inst

        # Map each instantiation to its own thread to minimuze http request blocking
        with ThreadPoolExecutor(max_workers=len(self._active_exchanges)) as executor:
            executor.map(
                _init_exchange_thread,
                self._exchange_class_map.keys(),
                self._exchange_class_map.values(),
                [kwargs] * len(self._exchange_class_map),
            )

    @property
    def log_level(self):
        return logging.getLogger("cryptomart").level

    @log_level.setter
    def log_level(self, level):
        logging.getLogger("cryptomart").setLevel(level)

    @property
    def exchanges(self):
        return [exchange_instance for exchange_enum, exchange_instance in self._exchange_instance_map.items()]
