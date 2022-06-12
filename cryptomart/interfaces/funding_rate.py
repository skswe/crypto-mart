import datetime
import os
from typing import Callable, Union

import numpy as np
import pandas as pd
from pyutil.cache import cached

from ..enums import FundingRateSchema, Instrument, Symbol
from ..errors import MissingDataError, NotSupportedError
from ..types import TimeType
from ..util import get_request_intervals, parse_time
from .api import APIInterface


class FundingRateInterface(APIInterface):
    """API interface to query funding rate data. Columns to be returned are defined in the `FundingRateSchema` enum."""

    def __init__(
        self,
        max_response_limit: Union[int, Callable[[datetime.timedelta], int]],
        valid_data_threshold: float = 1,
        funding_interval: datetime.timedelta = datetime.timedelta(hours=8),
        **api_interface_kwargs,
    ):
        """Initialize the interface

        Args:
            max_response_limit (int): Max number of rows that can be returned in one request to the API
            valid_data_threshold (float, optional): Percentage of data that must be present in the response. Depending on the
                value of `strict` in the function call, either a warning will be logged or an exception will be raised. Defaults to 1.
        """
        super().__init__(**api_interface_kwargs)
        self.instruments = self.exchange.instrument_info(self.inst_type, map_column=Instrument.exchange_symbol)
        self.max_response_limit = max_response_limit
        self.valid_data_threshold = valid_data_threshold
        self.funding_interval = funding_interval

    @cached(
        os.path.join(os.getenv("CM_CACHE_PATH", "/tmp/cache"), "funding_rate"),
        is_method=True,
        instance_identifiers=["name"],
    )
    def run(
        self,
        symbol: Symbol,
        starttime: TimeType,
        endtime: TimeType,
        strict: bool,
        **cache_kwargs,
    ) -> pd.DataFrame:
        """Run main interface function

        Args:
            symbol (Symbol): Symbol to query
            starttime (TimeType): Time of the first open
            endtime (TimeType): Time of the last close
            strict (bool): If `True`, raises an exception when missing data is above threshold
        Raises:
            NotSupportedError: If the given symbol is not supported by the API
            MissingDataError: If data does not meet self.valid_data_threshold and `strict=True`.

        Returns:
            pd.DataFrame: funding rate dataframe
        """
        starttime = parse_time(starttime)
        endtime = parse_time(endtime)
        assert endtime > starttime, "Invalid times"

        try:
            assert symbol in self.instruments
        except AssertionError as e:
            raise NotSupportedError(f"{self.name} does not support the given symbol or interval") from e

        instrument_id = self.instruments[symbol]
        limit = (
            self.max_response_limit
            if not callable(self.max_response_limit)
            else self.max_response_limit(self.funding_interval)
        )

        start_times, end_times, limits = get_request_intervals(
            starttime,
            endtime,
            self.funding_interval,
            limit,
        )
        self.logger.debug(f"start_times={start_times} | end_times={end_times} | limits={limits}")

        data = self.execute(self.dispatcher, self.url, instrument_id, start_times, end_times, limits)
        if data.empty:
            if strict:
                raise MissingDataError("No data available for specified time period")
            else:
                self.logger.warning("No data available for specified time period")
                return pd.DataFrame(
                    {FundingRateSchema.timestamp: pd.date_range(starttime, endtime, freq=self.funding_interval)[:-1]},
                    columns=FundingRateSchema._values(),
                )
        data = data.sort_values(FundingRateSchema.timestamp, ascending=True)
        data[FundingRateSchema.timestamp] = data[FundingRateSchema.timestamp].apply(lambda e: parse_time(e))
        data = data.set_index(FundingRateSchema.timestamp)

        data = data.resample(self.funding_interval).median()

        # Fill missing rows / remove extra rows
        # remove the last index since we only care about open_time
        expected_index = pd.date_range(starttime, endtime, freq=self.funding_interval)[:-1]

        # Drop duplicate open_time axis
        data = data.groupby(FundingRateSchema.timestamp).first()

        # Forces index to [starttime, endtime], adding nulls where necessary
        data = data.reindex(expected_index).reset_index().rename(columns={"index": FundingRateSchema.timestamp})

        # Convert columns to float
        data[np.setdiff1d(data.columns, FundingRateSchema.timestamp)] = data[
            np.setdiff1d(data.columns, FundingRateSchema.timestamp)
        ].astype(float)

        expected_n_rows = sum(limits)
        if len(data) < expected_n_rows:
            if (len(data) / expected_n_rows) > self.valid_data_threshold or len(data) == 0:
                msg = f"Missing {100 * (1 - (len(data) / expected_n_rows))}% of data"
                if strict:
                    raise MissingDataError(msg)
                else:
                    self.logger.warning(msg)

        return data
