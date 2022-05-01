import datetime

import pandas as pd

from .enums import InstrumentType, Interval, OHLCVColumn, Symbol


# Decorator to copy pandas DataFrame metadata for operations which pandas fails to implement
def copy_metadata(func):
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        for attr in self._metadata:
            setattr(result, attr, getattr(self, attr))
        return result

    return wrapper


class OHLCVBase(pd.DataFrame):
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


class OHLCVFeed(OHLCVBase):
    _metadata = ["exchange_name", "instType", "symbol", "interval", "orig_starttime", "orig_endtime"]

    def __init__(
        self,
        data=None,
        exchange_name: str = "",
        instType: InstrumentType = None,
        symbol: Symbol = None,
        interval: Interval = None,
        starttime: datetime = None,
        endtime: datetime = None,
    ):
        self.exchange_name = exchange_name
        self.instType = instType
        self.symbol = symbol
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
