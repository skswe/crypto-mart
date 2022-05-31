import datetime
import math
from typing import Callable, Dict, List, Tuple

import numpy as np
import pandas as pd
from pyutil.cache import cached
from requests import Request

from ..enums import Instrument, InstrumentType, Interval, OHLCVColumn, Symbol
from ..errors import MissingDataError, NotSupportedError
from ..interfaces.api import APIInterface
from ..types import IntervalType, JSONDataType, TimeType
from ..util import parse_time


class OrderBookInterface(APIInterface):
    def __init__(
        self,
        prepare_request: Callable[[str, str, int], Request],
        extract_data: Callable[[JSONDataType], pd.DataFrame],
        **api_interface_kwargs,
    ):
        super().__init__(**api_interface_kwargs)
        self.prepare_request = prepare_request
        self.extract_response = extract_data
        
    def run(self, symbol, depth=20) -> pd.DataFrame:
        req = self.prepare_request(self.url, symbol, depth)