import datetime
import logging
import os

import pandas as pd

from .enums import InstrumentType, Interval, OHLCVColumn, Symbol

logger = logging.getLogger(__name__)

# Decorator to copy pandas DataFrame metadata for operations which pandas fails to implement
def copy_metadata(func):
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        for attr in self._metadata:
            setattr(result, attr, getattr(self, attr))
        return result

    return wrapper


class FeedBase(pd.DataFrame):
    # Important note about subclassing a dataframe:
    # On some pandas dataframe operations, __init__ will be invoked with the original dataframe
    # as the first argument.
    # Thus, all subclasses of FeedBase that implement __init__ must have `data` as the
    # very first argument and also as a keyword argument. __init__ must handle the case
    # where this data kwarg is provided, and invoke the DataFrame constructor with super().__init__(data=data).

    # This also means that subclasses implementing __init__ must not take any position arguments. Since
    # a pandas operation might trigger __init__ without passing the expected position arguments.

    # You may also ask "What if my constructor requires keyword arguments which pandas does not supply
    # when __init__ is triggered?" Simply override and decorate any dataframe operations that trigger __init__
    # with `@copy_metadata`. This decorator will copy all of the attributes from the original dataframe to the
    # newly constructed dataframe after the resulting dataframe operation completes.
    @classmethod
    def _pandas_constructor(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    @property
    def _constructor(self):
        return self._pandas_constructor

    # Utility methods
    @property
    def earliest_time(self):
        if self.empty:
            return None

        return self[~self[OHLCVColumn.open].isna()].iloc[0][OHLCVColumn.open_time]

    @property
    def latest_time(self):
        if self.empty:
            return None

        return self[~self[OHLCVColumn.open].isna()].iloc[-1][OHLCVColumn.open_time]

    @property
    def missing_indices(self):
        return self[self[OHLCVColumn.open].isna()].index

    @property
    def missing_rows(self):
        return self.loc[self.missing_indices]

    @property
    def gaps(self):
        return (
            self[self[OHLCVColumn.open].notna()][OHLCVColumn.open_time]
            .diff()
            .pipe(lambda series: series[series > pd.Timedelta("1 days")])
            .count()
        )

    @property
    def _underlying_info(self):
        raise NotImplementedError

    @property
    def _df(self):
        return pd.DataFrame(self)

    @copy_metadata
    def merge(self, *args, **kwargs):
        return super().merge(*args, **kwargs)

    def display(self, columns=OHLCVColumn.open, **kwargs):
        if columns == "all":
            columns = [column.name for column in OHLCVColumn if column not in [OHLCVColumn.open_time]]
        return super().set_index(OHLCVColumn.open_time)[columns].plot(title=self._underlying_info, **kwargs)

    def __str__(self):
        return super().__str__() + self._underlying_info + "\n"


class OHLCVFeed(FeedBase):
    _metadata = ["exchange_name", "symbol", "instType", "interval", "orig_starttime", "orig_endtime"]

    def __init__(
        self,
        data=None,
        exchange_name: str = "",
        symbol: Symbol = None,
        instType: InstrumentType = None,
        interval: Interval = None,
        starttime: datetime.datetime = None,
        endtime: datetime.datetime = None,
    ):
        """Create an OHLCV Feed from a DataFrame. This class provides additional DataFrame operations and provides metadata about the feed.

        Args:
            data (pd.DataFrame, optional): Underlying dataframe object to wrap.
            exchange_name (str, optional): Name of the exchange this data is from. Defaults to "".
            symbol (Symbol, optional): Symbol for this data. Defaults to None.
            instType (InstrumentType, optional): InstrumentType for this data. Defaults to None.
            interval (Interval, optional): Interval for this data. Defaults to None.
            starttime (datetime.datetime, optional): Starttime for this data. Defaults to None.
            endtime (datetime.datetime, optional): Endtime for this data. Defaults to None.
        """
        self.exchange_name = exchange_name
        self.symbol = symbol
        self.instType = instType
        self.interval = interval
        self.orig_starttime = starttime
        self.orig_endtime = endtime

        if isinstance(data, pd.DataFrame):
            # Returns = the % gain on close from one bar to the next
            metric_column = data[OHLCVColumn.close]
            data[OHLCVColumn.returns] = ((metric_column - metric_column.shift(1)) / metric_column.shift(1)) * 100

        super().__init__(data=data)

    @property
    def _underlying_info(self):
        return f"{self.exchange_name}.{self.instType}.{self.symbol}"


class CSVFeed(OHLCVFeed):
    def __init__(
        self,
        data=None,
        path: str = "",
        exchange_name: str = "",
        symbol: str = "",
        instType: str = "",
        interval: str = "",
        column_map: dict = {},
    ):
        """Create a OHLCV data feed from CSV located at `path`.

        Args:
            data (pd.DataFrame, optional): (Internal use only) Underlying dataframe object to wrap.
            path (str): Path to CSV file
            exchange_name (str): Name of exchange this data is from
            symbol (str): Symbol for this data
            instType (str): Instrument type for this data
            interval (str): Interval for this data
            column_map (dict, optional): mapping override of OHLCVColumn to the name present in CSV data. Defaults to {}.
        """

        if data is not None:
            return super().__init__(data=data)

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
        starttime = df[df.open.notna()].iloc[0]["open_time"]
        endtime = df[df.open.notna()].iloc[-1]["open_time"]

        super().__init__(
            data=df,
            exchange_name=exchange_name,
            symbol=symbol,
            instType=instType,
            interval=interval,
            starttime=starttime,
            endtime=endtime,
        )

    @classmethod
    def from_directory(
        cls, root_path: str, exchange_name: str, symbol: str, instType: str, interval: str, column_map: dict = {}
    ):
        """Use this constructor to create a feed using a directory structured by `root/exchange_name/symbol/instType/interval.csv`

        Args:
            root_path (str): Root directory path for data directory
            exchange_name (str): name of exchange as it appears on disk
            symbol (str): name of symbol as it appears on disk
            instType (str): name of instType as it appears on disk
            interval (str): name of interval as it appears on disk
            column_map (dict, optional): mapping override of OHLCVColumn to the name present in CSV data. Defaults to {}.
        """

        file = os.path.exists(os.path.join(root_path, exchange_name, symbol, instType, f"{interval}.csv"))
        if not os.path.exists(file):
            raise FileNotFoundError("File not found:", file)

        return cls(file, exchange_name, symbol, instType, interval, column_map)
