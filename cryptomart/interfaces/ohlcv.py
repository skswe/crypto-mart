import datetime
import math
import os
from typing import Callable, Dict, List, Tuple, Union

import numpy as np
import pandas as pd
from cryptomart.feeds import OHLCVFeed
from pyutil.cache import cached

from ..enums import Instrument, Interval, OHLCVColumn, Symbol
from ..errors import MissingDataError, NotSupportedError
from ..interfaces.api import APIInterface
from ..types import IntervalType, TimeType
from ..util import parse_time


class OHLCVInterface(APIInterface):
    """API interface to query OHLCV data. Columns to be returned are defined in the `OHLCVColumn` enum."""

    def __init__(
        self,
        intervals: Dict[Interval, IntervalType],
        start_inclusive: bool,
        end_inclusive: bool,
        max_response_limit: Union[int, Callable[[datetime.timedelta], int]],
        valid_data_threshold: float = 1,
        **api_interface_kwargs,
    ):
        """Initialize the interface

        Args:
            intervals (Dict[Interval, IntervalType]): Mapping of `Interval` enum to API interval ID for the interface
            start_inclusive (bool): `True` if the first open_time returned will match starttime parameter
            end_inclusive (bool): `True` if the last open_time returned will match endtime parameter
            max_response_limit (int): Max number of rows that can be returned in one request to the API
            valid_data_threshold (float, optional): Percentage of data that must be present in the response. Depending on the
                value of `strict` in the function call, either a warning will be logged or an exception will be raised. Defaults to 1.
        """
        super().__init__(**api_interface_kwargs)
        self.instruments = self.exchange.instrument_info(self.inst_type, map_column=Instrument.exchange_symbol)
        self.intervals = intervals
        self.start_inclusive = start_inclusive
        self.end_inclusive = end_inclusive
        self.max_response_limit = max_response_limit
        self.valid_data_threshold = valid_data_threshold

    @cached(
        os.path.join(os.getenv("CM_CACHE_PATH", "/tmp/cache"), "ohlcv"),
        is_method=True,
        instance_identifiers=["name"],
    )
    def run(
        self,
        symbol: Symbol,
        interval: Interval,
        starttime: TimeType,
        endtime: TimeType,
        strict: bool,
        **cache_kwargs,
    ) -> pd.DataFrame:
        """Run main interface function

        Args:
            symbol (Symbol): Symbol to query
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

        start_times, end_times, limits = self.get_request_intervals(starttime, endtime, timedelta, limit)

        data = self.execute(self.dispatcher, self.url, instrument_id, interval_id, start_times, end_times, limits)

        data[OHLCVColumn.open_time] = data[OHLCVColumn.open_time].apply(lambda e: parse_time(e))

        # Fill missing rows / remove extra rows
        # remove the last index since we only care about open_time
        expected_index = pd.date_range(starttime, endtime, freq=timedelta)[:-1]

        # Drop duplicate open_time axis
        data = data.groupby(OHLCVColumn.open_time).first()

        # Forces index to [starttime, endtime], adding nulls where necessary
        data = data.reindex(expected_index).reset_index().rename(columns={"index": OHLCVColumn.open_time})

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

        return OHLCVFeed(data, self.exchange.name, symbol, self.inst_type, interval, starttime, endtime)

    def get_request_intervals(
        self,
        starttime: datetime.datetime,
        endtime: datetime.datetime,
        timedelta: datetime.timedelta,
        limit: int,
    ) -> Tuple[List[int], List[datetime.datetime], List[datetime.datetime]]:
        """Partition a time period into chunks of `timedelta * limit`

        Returns:
            Tuple[List[datetime.datetime], List[datetime.datetime], List[int]]: The starttime, endtime, count(timedelta) of each partition
        """
        effective_start_time, effective_end_time = self.snap_times(starttime, endtime, timedelta)

        # Adjust endpoints
        if self.start_inclusive == False:
            # Start time must be immediately before
            effective_start_time -= datetime.timedelta(seconds=1)
        if self.end_inclusive == True:
            # End time must be immediately before
            effective_end_time -= datetime.timedelta(seconds=1)

        cursor = effective_start_time
        start_times: List[datetime.datetime] = [cursor]
        end_times: List[datetime.datetime] = []
        limits = []
        while cursor < effective_end_time:
            cursor += limit * timedelta

            if cursor > effective_end_time:
                end_times.append(effective_end_time)
                final_limit = math.ceil((end_times[-1] - start_times[-1]) / timedelta)
                limits.append(final_limit)
            else:
                end_times.append(cursor)
                start_times.append(cursor)
                limits.append(limit)

        self.logger.debug(f"effective interval: ({effective_start_time}, {effective_end_time}), limits: {limits}")
        return start_times, end_times, limits

    @staticmethod
    def snap_times(
        a: datetime.datetime, b: datetime.datetime, interval: datetime.timedelta
    ) -> Tuple[datetime.datetime, datetime.datetime]:
        """Snap endpoints a and b to the time grid defined by `interval`

        Args:
            a (datetime.datetime): start time
            b (datetime.datetime): end time
            interval (datetime.timedelta): The time scale to snap times to

        Returns:
            Tuple[datetime.datetime, datetime.datetime]: Returns a new snapped interval of (a, b)
        """
        # datetime.datetime.min is the time origin (1, 1, 1, 0, 0)
        # the time grid is the sequence of `interval`'s since the time origin, starting at the origin
        # e.g. if `interval` is 1 day then the time grid is (1, 1, 1, 0, 0), (1, 2, 1, 0, 0), (1, 3, 1, 0, 0) ...
        # remainder is the amount of time past a datetime in the time grid
        time_min = datetime.datetime.min

        remainder = (a - time_min) % interval
        if remainder > datetime.timedelta(0):
            # bump starttime up to next datetime in the time grid
            starttime = a + (interval - remainder)
        else:
            starttime = a

        remainder = (b - time_min) % interval
        if remainder > datetime.timedelta(0):
            # bump endtime back to previous datetime in the time grid
            endtime = b - remainder
        else:
            endtime = b

        return starttime, endtime

    @classmethod
    def format_responses(
        cls, responses, data_attrs, code_attrs, expected_code, err_msg_attrs, col_map
    ) -> pd.DataFrame:
        """Automatically handle list of timeseries python parsed JSON responses"""
        out = pd.DataFrame(columns=col_map.values())
        for res in responses:
            try:
                df = cls.handle_response(res, data_attrs, code_attrs, expected_code, err_msg_attrs, col_map)
                out = pd.concat([out, df], ignore_index=True)
            except MissingDataError:
                continue
        return out.sort_values(OHLCVColumn.open_time, ascending=True)

    @staticmethod
    def parse_response(res: dict, col_map: dict) -> pd.DataFrame:
        """Format API response to standard dataframe"""
        df = pd.DataFrame(res)
        if df.empty:
            raise MissingDataError
        df.rename(columns=col_map, inplace=True)
        return df[col_map.values()]
