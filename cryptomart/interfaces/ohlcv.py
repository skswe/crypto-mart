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


class OHLCVInterface(APIInterface):
    """API interface to query OHLCV data. Columns to be returned are defined in the `OHLCVColumn` enum."""

    def __init__(
        self,
        instruments: Dict[Symbol, str],
        intervals: Dict[Interval, IntervalType],
        time_granularity: datetime.timedelta,
        start_inclusive: bool,
        end_inclusive: bool,
        max_response_limit: int,
        prepare_request: Callable[[str, str, IntervalType, TimeType, TimeType, int], Request],
        extract_data: Callable[[List[JSONDataType]], pd.DataFrame],
        valid_data_threshold: float = 1,
        **api_interface_kwargs,
    ):
        """Initialize the interface

        Args:
            instruments (Dict[Symbol, str]): Mapping of `Symbol` enum to API instrument ID for this interface
            intervals (Dict[Interval, IntervalType]): Mapping of `Interval` enum to API interval ID for the interface
            time_granularity (datetime.timedelta): The granularity of the time format the API uses. I.e. seconds / milliseconds
            start_inclusive (bool): `True` if the first open_time returned will match starttime parameter
            end_inclusive (bool): `True` if the last open_time returned will match endtime parameter
            max_response_limit (int): Max number of rows that can be returned in one request to the API
            prepare_request (Callable[[str, str, IntervalType, TimeType, TimeType, int], Request]): Function which takes
                (url, instrument_id, interval_id, starttime, endtime, limit) and returns a `Request` to be sent to the API
            extract_data (Callable[[List[JSONDataType]], pd.DataFrame]): Function which takes a list of all API responses and
                and returns a DataFrame in standard format. I.e. all columns in `OHLCVColumn` are present with the correct dtype.
            valid_data_threshold (float, optional): Percentage of data that must be present in the response. Depending on the
                value of `strict` in the function call, either a warning will be logged or an exception will be raised. Defaults to 1.
        """
        super().__init__(**api_interface_kwargs)
        self.instruments = instruments
        self.intervals = intervals
        self.time_granularity = time_granularity
        self.start_inclusive = start_inclusive
        self.end_inclusive = end_inclusive
        self.max_response_limit = max_response_limit
        self.prepare_request = prepare_request
        self.extract_data = extract_data
        self.valid_data_threshold = valid_data_threshold

    def run(
        self,
        symbol: Symbol,
        interval: Interval,
        starttime: TimeType,
        endtime: TimeType,
        disable_cache: bool,
        refresh_cache: bool,
        strict: bool,
    ) -> pd.DataFrame:
        """Run main interface function

        Args:
            symbol (Symbol): Symbol to query
            interval (Interval): Interval or frequency of bars
            starttime (TimeType): Time of the first open
            endtime (TimeType): Time of the last close
            disable_cache (bool): If `True`, disables data caching
            refresh_cache (bool): If `True`, refreshes the data cache with the latest result
            strict (bool): If `True`, raises an exception when missing data is above threshold

        Raises:
            NotSupportedError: _description_
            MissingDataError: _description_

        Returns:
            pd.DataFrame: _description_
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
        limit = self.max_response_limit

        start_times, end_times, limits = self.get_request_intervals(starttime, endtime, timedelta, limit)

        _requests = []
        for _starttime, _endtime, limit in zip(start_times, end_times, limits):
            request = self.prepare_request(self.url, instrument_id, interval_id, _starttime, _endtime, limit)
            _requests.append(request)

        responses = self.dispatcher.send_requests(_requests)
        data = self.extract_data(responses)

        data = self.format_df(data)

        expected_n_rows = sum(limits)
        if len(data) < expected_n_rows:
            if (len(data) / expected_n_rows) > self.valid_data_threshold or len(data) == 0:
                msg = f"Missing {100 * (1 - (len(data) / expected_n_rows))}% of data"
                if strict:
                    raise MissingDataError(msg)
                else:
                    self.logger.warning(msg)

        return data

    @cached("/tmp/cache/listing", is_method=True, instance_identifiers=["name"])
    def get_instrument_listing(
        self,
        symbol: Symbol,
        inst_type: InstrumentType,
        cache_kwargs={},
    ):
        """Return listing for a given instrument"""
        self.logger.info(f"Getting listing for {self.name}_earliest_{inst_type}_{symbol}")

        interval = Interval.interval_1d
        starttime = datetime.datetime(2018, 1, 1)
        endtime = datetime.datetime.now()
        symbol_name = self.get_instrument(symbol, inst_type)[Instrument.contract_name]
        interval_name, timedelta = self.intervals[interval]

        df = self._ohlcv(
            symbol_name,
            inst_type,
            interval_name,
            starttime,
            endtime,
            timedelta,
            exit_on_first_response=True,
            min_datapoints_required=5,
            strict=False,
            # Do not cache at ohlcv level
            cache_kwargs={"disabled": True, "refresh": False},
        )

        ret_val = df[~df.open.isna()].iloc[0][OHLCVColumn.open_time].to_pydatetime()

        return ret_val

    def format_df(
        self,
        data: pd.DataFrame,
        starttime: datetime.datetime,
        endtime: datetime.datetime,
        timedelta: datetime.timedelta,
    ) -> pd.DataFrame:

        # Fill missing rows / remove extra rows
        # remove the last index since we only care about open_time
        expected_index = pd.period_range(starttime, endtime, freq=timedelta)[:-1].to_timestamp()

        # Drop duplicate open_time axis
        data = data.groupby(OHLCVColumn.open_time).first()

        # Forces index to [starttime, endtime], adding nulls where necessary
        data = data.reindex(expected_index).reset_index().rename(columns={"index": OHLCVColumn.open_time})

        # Convert columns to float
        data[np.setdiff1d(data.columns, OHLCVColumn.open_time)] = data[
            np.setdiff1d(data.columns, OHLCVColumn.open_time)
        ].astype(float)

        return data

    def get_request_intervals(
        self,
        starttime: datetime.datetime,
        endtime: datetime.datetime,
        timedelta: datetime.timedelta,
        limit: int,
    ) -> Tuple[List[int], List[int], List[int]]:
        """Partition a time period into chunks of `timedelta * limit`, Converts datetime into millisecond.

        Args:
            starttime (datetime.datetime): Start time
            endtime (datetime.datetime): End time
            timedelta (datetime.timedelta):
            limit (int): [description]

        Returns:
            Tuple[List[int], List[int], List[int]]: The starttime, endtime, count(timedelta) of each partition
        """
        effective_start_time, effective_end_time = self.snap_times(starttime, endtime, timedelta)

        # Adjust endpoints
        if self.start_inclusive == False:
            # Start time must be immediately before
            effective_start_time -= datetime.timedelta(seconds=1)
        if self.end_inclusive == True:
            # End time must be immediately before
            effective_end_time -= datetime.timedelta(seconds=1)

        cursor = effective_start_time.timestamp()
        start_times: List[datetime.datetime] = [cursor]
        end_times: List[datetime.datetime] = []
        limits = []
        while cursor < effective_end_time.timestamp():
            cursor += int(limit * timedelta.total_seconds())

            if cursor > effective_end_time.timestamp():
                end_times.append(effective_end_time.timestamp())
                final_limit = math.ceil((end_times[-1].timestamp() - start_times[-1].timestamp()) / timedelta)
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

        remainder = (a - datetime.datetime.min) % interval
        if remainder > datetime.timedelta(0):
            # bump starttime up to next datetime in the time grid
            starttime = a + (interval - remainder)
        else:
            starttime = a

        remainder = (b - datetime.datetime.min) % interval
        if remainder > datetime.timedelta(0):
            # bump endtime back to previous datetime in the time grid
            endtime = b - remainder
        else:
            endtime = b

        return starttime, endtime
