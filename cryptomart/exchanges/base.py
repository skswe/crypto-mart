import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

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

    interfaces = {}

    def __init__(self, cache_kwargs: dict = {"disabled": False, "refresh": False}):
        """Init the exchange

        Args:
            cache_kwargs (dict, optional): Cache control settings. See pyutil.cache.cached for details.. Defaults to {"disabled": False, "refresh": False}.
        """
        self.logger = logging.getLogger(f"cryptomart.{self.name}")
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
        self.logger.debug(f"args={args} | kwargs={kwargs}")
        return self._get_interface(interface_name, inst_type).run(*args, **kwargs)

    def instrument_info(self, inst_type: InstrumentType, mappings: bool = False, cache_kwargs: dict = {}):
        args = (mappings,)
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
    ):
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

    def order_book(self, symbol: Symbol, inst_type: InstrumentType, depth: int, cache_kwargs: dict = {}):
        args = (symbol, depth)
        return self._run_interface(
            Interface.ORDER_BOOK, inst_type, *args, cache_kwargs=dict(self.cache_kwargs, **cache_kwargs)
        )
