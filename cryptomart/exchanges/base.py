import datetime
import logging
import math
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Union

import numpy as np
import pandas as pd
import requests
from pyutil.cache import cached
from pyutil.dicts import stack_dict

from ..enums import (
    Instrument,
    InstrumentType,
    Interface,
    Interval,
    OHLCVColumn,
    OrderBookSchema,
    OrderBookSide,
    Symbol,
)
from ..errors import MissingDataError, NotSupportedError
from ..feeds import OHLCVFeed
from ..globals import EARLIEST_OHLCV_DATE, END_OHLCV_DATE, INVALID_DATE
from ..interfaces.ohlcv import OHLCVInterface
from ..util import Dispatcher

logger = logging.getLogger(__name__)


class ExchangeAPIBase(ABC):
    @property
    @abstractmethod
    def name() -> str:
        pass

    @property
    @abstractmethod
    def interfaces() -> Dict[Interface, Dict[InstrumentType, OHLCVInterface]]:
        pass

    def __init__(self):
        self.logger = logging.getLogger(f"cryptomart.{self.name}")

    def _run_interface(self, interface_name, inst_type, *args):
        try:
            interface = self.interfaces[interface_name]
        except KeyError:
            self.logger.error(f"{self.name} does not support {interface_name}")

        try:
            interface = interface[inst_type]
        except KeyError:
            self.logger.error(f"{self.name}.{interface_name} does not support {inst_type}")

        return interface.run(*args)

    def instrument_info(self, inst_type):
        return self._run_interface(
            interface_name=Interface.INSTRUMENT_INFO,
            inst_type=inst_type,
        )

    def ohlcv(self, symbol, inst_type, interval, starttime, endtime):
        submit_args = (symbol, interval, starttime, endtime)
        return self._run_interface(interface_name=Interface.OHLCV, inst_type=inst_type, submit_args=submit_args)

    def order_book(self, symbol, inst_type, depth, log_level):
        submit_args = (symbol, depth, log_level)
        return self._run_interface(interface_name=Interface.ORDER_BOOK, inst_type=inst_type, submit_args=submit_args)

