from __future__ import annotations

import datetime
import logging
import os

import numpy as np
import pandas as pd

from .enums import FundingRateSchema, InstrumentType, Interval, OHLCVColumn, Symbol
from .util import parse_time

logger = logging.getLogger(__name__)

# Decorator to copy pandas DataFrame metadata for operations which pandas fails to implement
def copy_metadata(func):
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        for attr in self._metadata:
            setattr(result, attr, getattr(self, attr))
        return result

    return wrapper


class TSFeedBase(pd.DataFrame):
    # Important note about subclassing a dataframe:
    # On some pandas dataframe operations, __init__ will be invoked with the original dataframe
    # as with a keyword argument with name `data` or the first argument.
    # Thus, all subclasses of FeedBase that implement __init__ must have `data` as the
    # very first argument and also as a keyword argument. This also means that subclasses implementing
    # __init__ must not take any positional arguments. Since a pandas operation might trigger __init__
    # without passing the expected positional arguments.

    # You may also ask "What if my constructor requires keyword arguments which pandas does not supply
    # when __init__ is triggered?" Simply override and decorate any dataframe operations that trigger __init__
    # with `@copy_metadata`. This decorator will copy all of the attributes from the original dataframe to the
    # newly constructed dataframe after the resulting dataframe operation completes.
    _metadata = ["time_column", "value_column", "timedelta"]

    def __init__(self, data=None, time_column=None, value_column=None, timedelta=None, **kwargs):
        """Timeseries Feed Base - properties and methods for working with a DataFrame that represents some sort of constant time series

        Args:
            data: Underlying dataframe. Defaults to None.
            time_column: Column that contains the time index. Defaults to None.
            value_column: Column(s) that represents the value(s). Defaults to None.
        """
        super().__init__(data=data, **kwargs)

        self.time_column = time_column
        self.value_column = value_column
        self.timedelta = timedelta

    @classmethod
    def _pandas_constructor(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    @property
    def _constructor(self):
        return self._pandas_constructor

    # Utility methods
    @property
    def earliest_time(self):
        try:
            return self[~self[self.value_column].isna()].iloc[0][self.time_column]
        except IndexError:
            return None

    @property
    def latest_time(self):
        try:
            return self[~self[self.value_column].isna()].iloc[-1][self.time_column]
        except IndexError:
            return None

    @property
    def missing_indices(self):
        return self[self[self.value_column].isna()].index

    @property
    def missing_rows(self):
        return self.loc[self.missing_indices]

    @property
    def valid_indices(self):
        return self[self[self.value_column].notna()].index

    @property
    def valid_rows(self):
        return self.loc[self.valid_indices]

    @property
    def missing_rows(self):
        return self.loc[self.missing_indices]

    @property
    def gaps(self):
        return (
            self[self[self.value_column].notna()][self.time_column]
            .diff()
            .pipe(lambda series: series[series > self.timedelta])
            .count()
        )

    @property
    def values_only(self):
        return self[np.setdiff1d(self.columns, self.time_column)]

    @property
    def time_only(self):
        return self[self.time_column]

    @property
    def _underlying_info(self):
        raise NotImplementedError

    @property
    def _df(self):
        return pd.DataFrame(self)

    @copy_metadata
    def merge(self, *args, **kwargs) -> TSFeedBase:
        return super().merge(*args, **kwargs)

    def plot(self, *args, **kwargs):
        return (
            pd.DataFrame(self.set_index(self.time_column)).dropna().plot(*args, title=self._underlying_info, **kwargs)
        )

    def __str__(self):
        return super().__str__() + "\n" + self._underlying_info + "\n"


class OHLCVFeed(TSFeedBase):
    _metadata = TSFeedBase._metadata + [
        "exchange_name",
        "symbol",
        "inst_type",
        "interval",
        "orig_starttime",
        "orig_endtime",
    ]

    def __init__(
        self,
        data=None,
        exchange_name: str = "",
        symbol: Symbol = None,
        inst_type: InstrumentType = None,
        interval: Interval = None,
        timedelta: datetime.timedelta = None,
        starttime: datetime.datetime = None,
        endtime: datetime.datetime = None,
        **kwargs,
    ):
        """Create an OHLCV Feed from a DataFrame. This class provides additional DataFrame operations and provides metadata about the feed.

        Args:
            data (pd.DataFrame, optional): Underlying dataframe object to wrap.
            exchange_name (str, optional): Name of the exchange this data is from. Defaults to "".
            symbol (Symbol, optional): Symbol for this data. Defaults to None.
            inst_type (InstrumentType, optional): InstrumentType for this data. Defaults to None.
            interval (Interval, optional): Interval for this data. Defaults to None.
            timedelta (datetime.timedelta, optional): Timedelta for this data. Defaults to None.
            starttime (datetime.datetime, optional): Starttime for this data. Defaults to None.
            endtime (datetime.datetime, optional): Endtime for this data. Defaults to None.
        """
        super().__init__(
            data=data, time_column=OHLCVColumn.open_time, value_column=OHLCVColumn.open, timedelta=timedelta, **kwargs
        )

        self.exchange_name = exchange_name
        self.symbol = symbol
        self.inst_type = inst_type
        self.interval = interval
        self.orig_starttime = starttime
        self.orig_endtime = endtime

    @classmethod
    def from_csv(
        cls,
        path: str = "",
        exchange_name: str = "",
        symbol: str = "",
        inst_type: str = "",
        interval: str = "",
        column_map: dict = {},
    ) -> OHLCVFeed:
        """Create a OHLCV data feed from CSV located at `path`.

        Args:
            data (pd.DataFrame, optional): (Internal use only) Underlying dataframe object to wrap.
            path (str): Path to CSV file
            exchange_name (str): Name of exchange this data is from
            symbol (str): Symbol for this data
            inst_type (str): Instrument type for this data
            interval (str): Interval for this data
            column_map (dict, optional): mapping override of OHLCVColumn to the name present in CSV data. Defaults to {}.
        """
        # Default map of unified column name to column name present in CSV data
        _column_map = {
            OHLCVColumn.open_time: "open_time",
            OHLCVColumn.open: "open",
            OHLCVColumn.high: "high",
            OHLCVColumn.low: "low",
            OHLCVColumn.close: "close",
            OHLCVColumn.volume: "volume",
        }

        # Update default map with user provided mappings
        _column_map.update(column_map)

        df = pd.read_csv(path)

        df = df.rename(columns=_column_map).reindex(columns=_column_map.keys())

        df = df.sort_values(OHLCVColumn.open_time, ascending=True)

        df[OHLCVColumn.open_time] = df[OHLCVColumn.open_time].apply(lambda e: parse_time(e))
        starttime = df.iloc[0][OHLCVColumn.open_time]
        endtime = df.iloc[-1][OHLCVColumn.open_time]
        timedelta = df[OHLCVColumn.open_time].diff().quantile(0).to_pytimedelta()

        # Fill missing rows / remove extra rows
        # remove the last index since we only care about open_time
        expected_index = pd.date_range(starttime, endtime, freq=timedelta)[:-1]

        # Drop duplicate open_time axis
        df = df.groupby(OHLCVColumn.open_time).first()

        # Forces index to [starttime, endtime], adding nulls where necessary
        df = df.reindex(expected_index).reset_index().rename(columns={"index": OHLCVColumn.open_time})

        # Convert columns to float
        df[np.setdiff1d(df.columns, OHLCVColumn.open_time)] = df[
            np.setdiff1d(df.columns, OHLCVColumn.open_time)
        ].astype(float)

        return cls(
            data=df,
            exchange_name=exchange_name,
            symbol=symbol,
            inst_type=inst_type,
            interval=interval,
            timedelta=timedelta,
            starttime=starttime,
            endtime=endtime,
        )

    @classmethod
    def from_directory(
        cls, root_path: str, exchange_name: str, symbol: str, inst_type: str, interval: str, column_map: dict = {}
    ) -> OHLCVFeed:
        """Use this constructor to create a feed using a directory structured by `root/exchange_name/symbol/inst_type/interval.csv`

        Args:
            root_path (str): Root directory path for data directory
            exchange_name (str): name of exchange as it appears on disk
            symbol (str): name of symbol as it appears on disk
            inst_type (str): name of inst_type as it appears on disk
            interval (str): name of interval as it appears on disk
            column_map (dict, optional): mapping override of OHLCVColumn to the name present in CSV data. Defaults to {}.
        """

        file = os.path.exists(os.path.join(root_path, exchange_name, symbol, inst_type, f"{interval}.csv"))
        if not os.path.exists(file):
            raise FileNotFoundError("File not found:", file)

        return cls.from_csv(file, exchange_name, symbol, inst_type, interval, column_map)

    @property
    def _underlying_info(self):
        return f"ohlcv.{self.exchange_name}.{self.inst_type}.{self.symbol}"


class FundingRateFeed(TSFeedBase):
    _metadata = TSFeedBase._metadata + ["exchange_name", "symbol", "orig_starttime", "orig_endtime"]

    def __init__(
        self,
        data=None,
        exchange_name: str = "",
        symbol: Symbol = None,
        timedelta: datetime.timedelta = None,
        starttime: datetime.datetime = None,
        endtime: datetime.datetime = None,
        **kwargs,
    ):
        """Create an Funding Rate Feed from a DataFrame. This class provides additional DataFrame operations and provides metadata about the feed.

        Args:
            data (pd.DataFrame, optional): Underlying dataframe object to wrap.
            exchange_name (str, optional): Name of the exchange this data is from. Defaults to "".
            symbol (Symbol, optional): Symbol for this data. Defaults to None.
            timedelta (datetime.timedelta, optional): Timedelta for this data. Defaults to None.
            starttime (datetime.datetime, optional): Starttime for this data. Defaults to None.
            endtime (datetime.datetime, optional): Endtime for this data. Defaults to None.
        """
        super().__init__(
            data=data,
            time_column=FundingRateSchema.timestamp,
            value_column=FundingRateSchema.funding_rate,
            timedelta=timedelta,
            **kwargs,
        )

        self.exchange_name = exchange_name
        self.symbol = symbol
        self.orig_starttime = starttime
        self.orig_endtime = endtime

    @property
    def _underlying_info(self):
        return f"funding_rate.{self.exchange_name}.{self.symbol}"
