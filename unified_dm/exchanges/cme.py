import datetime
import logging
import os

import numpy as np
import pandas as pd

from ..enums import InstrumentType, Interval
from ..feeds import OHLCVColumn
from .bases import ExchangeBase
from .instrument_names.cme import instrument_names as cme_instrument_names

logger = logging.getLogger(__name__)


class CME(ExchangeBase):

    name = "cme"

    instrument_names = {**cme_instrument_names}

    intervals = {
        Interval.interval_1d: ("1D", datetime.timedelta(days=1)),
    }

    _ohlcv_column_map = {
        "open_time": OHLCVColumn.open_time,
        "open": OHLCVColumn.open,
        "high": OHLCVColumn.high,
        "low": OHLCVColumn.low,
        "close": OHLCVColumn.close,
    }

    _data_path = "data/CME"

    @staticmethod
    def ET_to_datetime(et):
        return pd.to_datetime(et)

    def _ohlcv(
        self,
        instType: InstrumentType,
        symbol: str,
        interval: str,
        starttime: datetime.datetime,
        endtime: datetime.datetime,
        timedelta: datetime.timedelta,
        **kwargs,
    ) -> pd.DataFrame:
        raw_data = pd.read_csv(os.path.join(self._data_path, interval, symbol))
        return self._ohlcv_res_to_dataframe(raw_data, starttime, endtime, timedelta)

    def _ohlcv_res_to_dataframe(
        self,
        data: pd.DataFrame,
        starttime: datetime.datetime,
        endtime: datetime.datetime,
        timedelta: datetime.timedelta,
    ):
        data = super()._ohlcv_res_to_dataframe(data, starttime, endtime, timedelta)

        # Volume column is not present
        data[OHLCVColumn.volume] = np.nan

        return data
