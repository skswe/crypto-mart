import datetime

import numpy as np
import pandas as pd
from IPython.display import display

from .enums import InstrumentType, Interval, OHLCVColumn, SpreadColumn, Symbol

pd.options.plotting.backend = "plotly"

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

    # Statistical methods
    @property
    def volatility(self):
        DAYS_IN_YEAR = 365
        return self[OHLCVColumn.returns].std() * np.sqrt(DAYS_IN_YEAR)

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

    def show(self):
        print(self._underlying_info)
        display(self)


class OHLCVFeed(OHLCVBase):
    _metadata = ["exchange_name", "fee_info", "instType", "symbol", "interval", "orig_starttime", "orig_endtime"]

    def __init__(
        self,
        data=None,
        exchange_name: str = "",
        fee_info: dict = None,
        instType: InstrumentType = None,
        symbol: Symbol = None,
        interval: Interval = None,
        starttime: datetime = None,
        endtime: datetime = None,
    ):
        self.exchange_name = exchange_name
        self.fee_info = fee_info
        self.instType = instType
        self.symbol = symbol
        self.interval = interval
        self.orig_starttime = starttime
        self.orig_endtime = endtime

        if isinstance(data, pd.DataFrame):
            # Create returns column as ((Spread level 1/ Spread level 0) - 1) * 100
            metric_column = data[OHLCVColumn.close]
            data[OHLCVColumn.returns] = ((metric_column - metric_column.shift(1)) / metric_column.shift(1)) * 100

        super().__init__(data=data)

    @property
    def _underlying_info(self):
        return f"{self.exchange_name}.{self.instType.name}.{self.symbol.name}"

    def value_at_risk(self, percentile=5):
        temp = self[OHLCVColumn.returns]
        temp = temp[temp.notna()]
        temp = temp.sort_values()
        index = (percentile / 100) * (len(temp) + 1)
        floor_index = int(np.floor(index))
        ceiling_index = int(np.ceil(index))
        if floor_index != index:
            value_at_risk = (temp.iloc[floor_index] + temp.iloc[ceiling_index]) / 2
        else:
            value_at_risk = temp.iloc[floor_index]
        return value_at_risk


class Spread(OHLCVBase):
    _metadata = ["ohlcv_a", "ohlcv_b"]

    def __init__(self, data=None, a: OHLCVFeed = None, b: OHLCVFeed = None, z_score_period=30):
        if a is not None and b is not None:
            merged = b._df.merge(a._df, on=OHLCVColumn.open_time, suffixes=("_b", "_a"))
            data = pd.DataFrame()
            data[SpreadColumn.open_time] = merged[OHLCVColumn.open_time]
            data[SpreadColumn.open] = merged[OHLCVColumn.open + "_b"] - merged[OHLCVColumn.open + "_a"]
            data[SpreadColumn.high] = merged[OHLCVColumn.high + "_b"] - merged[OHLCVColumn.high + "_a"]
            data[SpreadColumn.low] = merged[OHLCVColumn.low + "_b"] - merged[OHLCVColumn.low + "_a"]
            data[SpreadColumn.close] = merged[OHLCVColumn.close + "_b"] - merged[OHLCVColumn.close + "_a"]
            data[SpreadColumn.volume] = (merged[OHLCVColumn.volume + "_b"] + merged[OHLCVColumn.volume + "_a"]) / 2
            data[SpreadColumn.returns] = merged[OHLCVColumn.returns + "_b"] - merged[OHLCVColumn.returns + "_a"]

            start_time = max(a.earliest_time, b.earliest_time)
            end_time = min(a.latest_time, b.latest_time)

            data = data[data[SpreadColumn.open_time].between(start_time, end_time)]
            metric_column = data[OHLCVColumn.close]
            data[SpreadColumn.zscore] = (
                metric_column - metric_column.rolling(z_score_period).mean()
            ) / metric_column.rolling(z_score_period).std()

        self.ohlcv_a = a
        self.ohlcv_b = b

        super().__init__(data=data)

    @property
    def underlyings(self):
        a = self.ohlcv_a[np.isin(self.ohlcv_a[OHLCVColumn.open_time], self[SpreadColumn.open_time])].reset_index(
            drop=True
        )
        b = self.ohlcv_b[np.isin(self.ohlcv_b[OHLCVColumn.open_time], self[SpreadColumn.open_time])].reset_index(
            drop=True
        )
        return pd.concat([a._df, b._df], keys=[a._underlying_info, b._underlying_info], axis=1)

    def underlying_col(self, column_name=SpreadColumn.close):
        index = self[SpreadColumn.open_time]
        df = self.underlyings.droplevel(0, axis=1)[column_name].set_axis(
            self.underlyings.columns.get_level_values(0).unique(), axis=1
        )
        df.index = index
        return df

    @property
    def _underlying_info(self):
        return f"{self.ohlcv_b._underlying_info} - {self.ohlcv_a._underlying_info}"

    def __str__(self):
        return super().__str__() + self._underlying_info + "\n"

    def profile(self):
        self.show()
        display(self.underlyings)
        self.ohlcv_a.show()
        display(self.ohlcv_a.orig_starttime, self.ohlcv_a.orig_endtime)
        self.ohlcv_b.show()
        display(self.ohlcv_b.orig_starttime, self.ohlcv_b.orig_endtime)
