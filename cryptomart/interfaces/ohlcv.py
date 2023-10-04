import datetime
import os
from typing import Callable, Dict, Union

import numpy as np
import pandas as pd

from ..enums import Interval, OHLCVColumn
from ..errors import MissingDataError, NotSupportedError
from ..feeds import OHLCVFeed
from ..interfaces.api import APIInterface
from ..types import IntervalType, TimeType
from ..util import cached, get_request_intervals, parse_time


class OHLCVInterface(APIInterface):
    """API interface to query OHLCV data. Columns to be returned are defined in the `OHLCVColumn` enum."""

    def __init__(
        self,
        instruments: Dict[str, str],
        intervals: Dict[Interval, IntervalType],
        max_response_limit: Union[int, Callable[[datetime.timedelta], int]],
        valid_data_threshold: float = 1,
        close_timestamp: bool = False,
        **api_interface_kwargs,
    ):
        """Initialize the interface

        Args:
            refresh_instruments (bool): If True, refreshes the instrument cache
            intervals (Dict[Interval, IntervalType]): Mapping of `Interval` enum to API interval ID for the interface
            max_response_limit (int): Max number of rows that can be returned in one request to the API
            valid_data_threshold (float, optional): Percentage of data that must be present in the response. Depending on the
                value of `strict` in the function call, either a warning will be logged or an exception will be raised. Defaults to 1.
        """
        super().__init__(**api_interface_kwargs)
        self.instruments = instruments
        self.intervals = intervals
        self.max_response_limit = max_response_limit
        self.valid_data_threshold = valid_data_threshold
        self.close_timestamp = close_timestamp

    @cached(
        os.path.join(os.getenv("CM_CACHE_PATH", "/tmp/cache"), "ohlcv"),
        instance_identifiers=["name"],
        instance_path_seperators=["exchange_name", "inst_type"],
        name="ohlcv",
    )
    def run(
        self,
        symbol: str,
        interval: Interval,
        starttime: TimeType,
        endtime: TimeType,
        strict: bool,
        **cache_kwargs,
    ) -> pd.DataFrame:
        """Run main interface function

        Args:
            symbol (str): Symbol to query
            interval (Interval): Interval or frequency of bars
            starttime (TimeType): Time of the first open
            endtime (TimeType): Time of the last close
            strict (bool): If `True`, raises an exception when missing data is above threshold
        Raises:
            NotSupportedError: If the given symbol, interval are not supported by the API
            MissingDataError: If data does not meet self.valid_data_threshold and `strict=True`.

        Returns:
            pd.DataFrame: OHLCV dataframe
        """
        starttime = parse_time(starttime)
        endtime = parse_time(endtime)
        if self.close_timestamp:
            starttime = starttime - self.intervals[interval][1]
        assert endtime > starttime, "Invalid times"

        try:
            assert symbol in self.instruments
            assert interval in self.intervals
        except AssertionError as e:
            raise NotSupportedError(f"{self.name} does not support the given symbol or interval") from e

        instrument_id = self.instruments[symbol]
        interval_id, timedelta = self.intervals[interval]
        limit = (
            self.max_response_limit if not callable(self.max_response_limit) else self.max_response_limit(timedelta)
        )

        start_times, end_times, limits = get_request_intervals(starttime, endtime, timedelta, limit)
        self.logger.debug(f"start_times={start_times} | end_times={end_times} | limits={limits}")

        data = self.execute(self.dispatcher, self.url, instrument_id, interval_id, start_times, end_times, limits)
        if data.empty:
            if strict:
                raise MissingDataError("No data available for specified time period")
            else:
                self.logger.warning("No data available for specified time period")
                return OHLCVFeed(
                    pd.DataFrame(
                        {OHLCVColumn.open_time: pd.date_range(starttime, endtime, freq=timedelta)[:-1]},
                        columns=OHLCVColumn._values(),
                    ),
                    self.exchange.name,
                    symbol,
                    self.inst_type,
                    interval,
                    timedelta,
                    starttime,
                    endtime,
                )
        data = data.sort_values(OHLCVColumn.open_time, ascending=True)

        data[OHLCVColumn.open_time] = data[OHLCVColumn.open_time].apply(lambda e: parse_time(e))

        # Fill missing rows / remove extra rows
        # remove the last index since we only care about open_time
        if not self.close_timestamp:
            expected_index = pd.date_range(starttime, endtime, freq=timedelta)[:-1]
        else:
            expected_index = pd.date_range(starttime, endtime, freq=timedelta)

        # Drop duplicate open_time axis
        data = data.groupby(OHLCVColumn.open_time).first()

        # Forces index to [starttime, endtime], adding nulls where necessary
        data = data.reindex(expected_index).reset_index().rename(columns={"index": OHLCVColumn.open_time})

        if self.close_timestamp:
            data[np.setdiff1d(data.columns, OHLCVColumn.open_time)] = data[
                np.setdiff1d(data.columns, OHLCVColumn.open_time)
            ].shift(-1)
            data = data[1:-1]

        # Convert columns to float
        data[np.setdiff1d(data.columns, OHLCVColumn.open_time)] = data[
            np.setdiff1d(data.columns, OHLCVColumn.open_time)
        ].astype(float)

        expected_n_rows = sum(limits)
        if len(data) < expected_n_rows:
            if (len(data) / expected_n_rows) > self.valid_data_threshold or len(data) == 0:
                msg = f"Missing {100 * (1 - (len(data) / expected_n_rows))}% of data"
                if strict:
                    raise MissingDataError(msg)
                else:
                    self.logger.warning(msg)

        return OHLCVFeed(data, self.exchange.name, symbol, self.inst_type, interval, timedelta, starttime, endtime)
