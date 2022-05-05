import datetime
import logging
import math
import time
from abc import ABC, abstractmethod
from sqlite3 import Row
from typing import Callable, Dict, List, Tuple, Union

import numpy as np
import pandas as pd
import requests
from requests import Request

from ..enums import (
    FeeInfo,
    FundingRateSchema,
    Instrument,
    InstrumentType,
    Interval,
    OHLCVColumn,
    OrderBookSchema,
    OrderBookSide,
    Symbol,
)
from ..feeds import OHLCVFeed
from ..globals import BLACKLISTED_SYMBOLS, EARLIEST_OHLCV_DATE, END_OHLCV_DATE, INVALID_DATE
from ..util import Dispatcher, cached, stack_dict

logger = logging.getLogger(__name__)


class MissingDataError(Exception):
    """Data is unexpectedly missing from an API call"""

    pass


class NotSupportedError(Exception):
    """Exchange does not support a built-in Enum"""

    pass


class AbstractExchangeBase(ABC):
    """Properties and methods that must be defined in all exchanges"""

    @property
    @abstractmethod
    def name() -> str:
        """Exchange name"""
        pass

    @property
    @abstractmethod
    def instrument_names() -> Dict[InstrumentType, Dict[Symbol, str]]:
        """2 layer mapping of InstrumentType -> Symbol -> Instrument name"""
        pass

    @property
    @abstractmethod
    def intervals() -> Dict[Interval, Tuple[Union[str, int], datetime.timedelta]]:
        """Mapping of Interval -> (interval exchange representation, interval timedelta representation)"""
        pass

    @property
    @abstractmethod
    def _ohlcv_column_map() -> Dict[Union[int, str], str]:
        """Mapping of Exchange OHLCV column representation -> standard OHLCV column names"""
        pass

    @property
    @abstractmethod
    def _funding_rate_column_map() -> Dict[Union[int, str], str]:
        """Mapping of Exchange Funding Rate column representation -> standard Funding Rate column names"""
        pass

    @abstractmethod
    def _ohlcv(
        self,
        instType: InstrumentType,
        symbol: str,
        interval: Union[str, int],
        starttime: datetime.datetime,
        endtime: datetime.datetime,
        timedelta: datetime.timedelta,
        exit_on_first_response: bool = False,
        min_datapoints_required: int = 0,
        strict: bool = False,
        use_cache: bool = True,
        refresh_cache: bool = False,
    ) -> pd.DataFrame:
        """Internal method to perform API requests

        Args:
            instType (InstrumentType): Instrument Type
            symbol (str): exchange specific symbol string
            interval (Union[str, int]): exchange specific interval representation
            starttime (datetime.datetime): start time
            endtime (datetime.datetime): end time
            timedelta (datetime.timedelta): datetime representation of `interval`
            strict (bool): if True, MissingDataError will raise an error, if False, only a warning will be logged
            exit_on_first_response (bool): stop making requests once a single datapoint is received from the API. Defaults to False.
            min_datapoints_required (int): minimum number of datapoints required to exit on first response. Defaults to 0.
            use_cache (bool): use cache (provided by @cached decorator)
            refresh_cache (bool): refresh cache (provided by @cached decorator)

        Raises:
            MissingDataError: if (receieved datapoints / expected datapoints) exceeds self._missing_data_threshold

        Returns:
            (pd.DataFrame): OHLCV DataFrame
        """
        pass


class AbstractExchangeAPIBase(AbstractExchangeBase):
    """Properties and methods that must be defined in all exchanges that query a public API"""

    @property
    @abstractmethod
    def _base_url() -> str:
        """API Base URL for all http requests"""
        pass

    @property
    @abstractmethod
    def _max_requests_per_second() -> float:
        """Max requests per second without getting IP restricted"""
        pass

    @property
    @abstractmethod
    def _limit() -> int:
        """Maximum number of datapoints returned in a request"""
        pass

    @property
    @abstractmethod
    def _start_inclusive() -> bool:
        """The first open_time returned will match starttime parameter"""
        pass

    @property
    @abstractmethod
    def _end_inclusive() -> bool:
        """The last open_time returned will match endtime parameter"""
        pass

    @abstractmethod
    def _ohlcv_prepare_request(self, instType, symbol, interval, starttime, endtime, limit) -> Request:
        """Function to set up API http request"""
        pass

    @abstractmethod
    def _ohlcv_extract_response(self, response) -> Union[List, dict]:
        """Function to extract data from API http response"""
        pass

    @abstractmethod
    def _order_book_prepare_request(self, instType, symbol, depth=50) -> Request:
        """Function to set up API http request"""
        pass

    @abstractmethod
    def _order_book_extract_response(self, response) -> Union[List, dict]:
        """Function to extract data from API http response"""
        pass

    @abstractmethod
    def _order_book_quantity_multiplier(self, instType, symbol) -> float:
        """Multiplier to bring order book size equal to size in underlying crypto asset"""
        pass

    @abstractmethod
    def order_book(self, symbol: Symbol, instType: InstrumentType, depth: int):
        """Return order book snapshot for given instrument"""
        pass

    @abstractmethod
    def _histrorical_funding_rate_prepare_request(self, instType, symbol, starttime, endtime, limit) -> Request:
        """Function to set up API request"""
        pass

    @abstractmethod
    def _histrorical_funding_rate_extract_response(self, response) -> Union[List, dict]:
        """Function to extract data from API http response"""
        pass

    # @abstractmethod
    # def historical_funding_rate(self, symbol: Symbol, starttime: datetime.datetime, endtime: datetime.datetime, instType: InstrumentType):
    #    """Return Funding Rate for given instrument"""


class ExchangeBase(AbstractExchangeBase):
    """Common base to house exchange data structures"""

    def __init__(
        self,
        debug: bool = False,
        use_instruments_cache: bool = True,
        refresh_instruments_cache: bool = False,
    ):
        if debug:
            self.log_level = logging.DEBUG

        self.all_instruments = pd.DataFrame(stack_dict(self.instrument_names)).rename(
            columns={
                0: Instrument.instType,
                1: Instrument.symbol,
                2: Instrument.contract_name,
            },
        )
        """All instruments that exist in the Exchange API"""

        # This property includes instruments that may be blacklisted. See globals.BLACKLISTED_SYMBOLS.
        # To access non-blacklisted active instruments, access the active_instruments property
        self._active_instruments = self.all_instruments.copy()

        # Load active instruments as the set of instruments that have a valid listing date
        # Defined as function so result can be cached
        @cached(
            "cache/instruments",
            additional_args=[self.name],
            active=use_instruments_cache,
            refresh=refresh_instruments_cache,
        )
        def load_active_instruments():
            logger.debug(f"Active instruments before getting listings: \n {self.active_instruments.head(20)}")
            self._active_instruments[Instrument.listing_date] = self._active_instruments.apply(
                lambda r: self._ohlcv_get_instrument_listing(r.instType, r.symbol), axis=1
            )
            logger.debug(f"Active instruments after getting listings: \n {self._active_instruments.head(20)}")
            self._active_instruments = self._active_instruments[
                self._active_instruments[Instrument.listing_date] != INVALID_DATE
            ]
            logger.debug(f"Active instruments after dropping rows: \n {self._active_instruments.head(20)}")
            return self._active_instruments

        self._active_instruments = load_active_instruments()

    @property
    def log_level(self):
        return logger.level

    @log_level.setter
    def log_level(self, level):
        logger.setLevel(level)

    @property
    def fee_pct(self):
        return 0

    @property
    def fee_fixed(self):
        return 0

    @property
    def slippage(self):
        return 0

    @property
    def init_margin(self):
        return 0

    @property
    def maint_margin(self):
        return 0.25

    @property
    def fee_info(self):
        return {k: getattr(self, k) for k in FeeInfo.names()}

    @property
    def instrument_types(self):
        """List of active instrument types"""
        return list(self.active_instruments[Instrument.instType].unique())

    @property
    def active_instruments(self):
        """All non-blacklisted instruments that exist in Exchange API and have OHLCV data"""
        return self._active_instruments[~np.isin(self._active_instruments[Instrument.symbol], BLACKLISTED_SYMBOLS)]

    def symbols(self, instType):
        """List of active symbols for the instrument type"""
        return list(
            self.active_instruments[self.active_instruments[Instrument.instType] == instType][Instrument.symbol]
        )

    def get_instrument(self, instType, symbol) -> pd.Series:
        """Returns active instrument for instType and symbol, raises error if the instrument does not exist"""
        try:
            return self.active_instruments[
                (self.active_instruments[Instrument.instType] == instType)
                & (self.active_instruments[Instrument.symbol] == symbol)
            ].iloc[0]
        except IndexError:
            raise IndexError(
                f"The given combination {instType}, {symbol} is not a valid instrument for {self.name}. Valid options are: \n\n{self.active_instruments}"
            ) from None

    def has_instrument(self, instType, symbol):
        """Returns true if the instrument exists in self.active_instruments"""
        try:
            self.get_instrument(instType, symbol)
            return True
        except IndexError:
            return False

    @property
    def missing_instruments(self):
        """Returns instruments that do not have a listing date"""
        return self.active_instruments.merge(self.all_instruments, how="right").pipe(
            lambda df: df[df[Instrument.listing_date].isna()]
        )[[Instrument.instType, Instrument.symbol, Instrument.contract_name]]

    def _parse_instrument(
        self, instType: Union[InstrumentType, str], symbol: Union[Symbol, str]
    ) -> Tuple[InstrumentType, Symbol]:
        """Function to enable convenience passing of strings to functions that expect InstrumentType and Symbol"""
        if isinstance(instType, str):
            try:
                instType = InstrumentType[instType.upper()]
            except KeyError:
                raise NotSupportedError(
                    f"{self.name} does not support {instType}. Must be one of {self.instrument_types}"
                )

        if isinstance(symbol, str):
            try:
                symbol = Symbol[symbol.upper()]
            except:
                raise NotSupportedError(
                    f"{self.name} does not support {symbol}. Must be one of {self.symbols(instType)}"
                )

        return instType, symbol

    def _ohlcv_validate(
        self,
        instType: InstrumentType,
        symbol: Symbol,
        interval: Interval,
        starttime: datetime.datetime,  # starttime is the open time of the very first bar
        endtime: datetime.datetime,  # endtime is the time that occurs immediately after the final close time:
    ):
        """Validate parameters passed to ohlcv method"""
        invalid_instType_msg = f"{self.name} does not support {instType}. Must be one of {self.instrument_types}"
        invalid_symbol_msg = f"{self.name} does not support {symbol}. Must be one of {self.symbols(instType)}"
        invalid_interval_msg = f"Interval must be one of {self.intervals.keys()}"

        instType, symbol = self._parse_instrument(instType, symbol)

        if isinstance(interval, str):
            try:
                interval = Interval[f"interval_{interval}"]
            except KeyError:
                raise NotSupportedError(invalid_interval_msg)

        if isinstance(starttime, tuple):
            starttime = datetime.datetime(*starttime)
        if isinstance(endtime, tuple):
            endtime = datetime.datetime(*endtime)
        starttime = self._ohlcv_get_default_starttime(starttime, instType, symbol)
        endtime = endtime or END_OHLCV_DATE
        try:
            assert instType in self.instrument_types, invalid_instType_msg
            assert self.has_instrument(instType, symbol), invalid_symbol_msg
            assert interval in self.intervals, invalid_interval_msg
        except AssertionError as e:
            raise NotSupportedError(e) from None

        assert isinstance(starttime, datetime.datetime), f"starttime must be a datetime"
        assert isinstance(endtime, datetime.datetime), f"endtime must be a datetime"
        assert endtime > starttime, "Invalid endtime"
        return instType, symbol, interval, starttime, endtime

    def _ohlcv_get_default_starttime(self, starttime, instType, symbol):
        """Returns listing date for given instrument if starttime is none"""
        listing_date = self.get_instrument(instType, symbol)[Instrument.listing_date].to_pydatetime()
        if starttime is None:
            logger.info("starttime is None, defaulting to instrument listing time")
            return listing_date
        if starttime < listing_date:
            logger.warning(f"Provided start time ({starttime}) is before instrument listing date: {listing_date}")
        return starttime

    def _ohlcv_res_to_dataframe(
        self,
        data: Union[List[Union[dict, list]], pd.DataFrame],
        starttime: datetime.datetime,
        endtime: datetime.datetime,
        timedelta: datetime.timedelta,
        time_column: str = "open_time",
    ) -> pd.DataFrame:
        """Convert list of datapoints from OHLCV API call to standard OHLCV DataFrame, using `column_map`

        Args:
            data (List[Union[dict, list]]): API Reponse
            starttime (datetime.datetime): starttime to snap DataFrame to
            endtime (datetime.datetime): endtime to snap DataFrame to
            timedelta (datetime.timedelta): timedelta to compute snapping logic
            time_column (str): whether to use open_time or close_time as main time index

        Returns:
            (pd.DataFrame): datframe with columns: [open_time, open, high, low, close, volume]
        """
        if isinstance(data, pd.DataFrame):
            # Response already formatted as dataframe
            pass
        elif isinstance(data[0], list) or isinstance(data[0], np.ndarray):
            # Response has unlabeled data (list)
            data = np.array(data)[:, list(self._ohlcv_column_map.keys())]
            data = pd.DataFrame(data, columns=list(self._ohlcv_column_map.values()))
        else:
            # Response has labeled data (dict)
            data: pd.DataFrame = pd.DataFrame(data)
            data.rename(columns=self._ohlcv_column_map, inplace=True)
            data = data[self._ohlcv_column_map.values()]

        # Convert open_time to datetime
        if time_column == "close_time":
            data.loc[:, OHLCVColumn.open_time] = data.loc[:, OHLCVColumn.open_time].apply(
                lambda e: self.ET_to_datetime(e) - timedelta
            )

        elif time_column == "open_time":
            data.loc[:, OHLCVColumn.open_time] = data.loc[:, OHLCVColumn.open_time].apply(
                lambda e: self.ET_to_datetime(e)
            )

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

    def _funding_rate_res_to_dataframe(
        self,
        data: Union[Union[dict, list], pd.DataFrame],
    ) -> pd.DataFrame:

        if isinstance(data, pd.DataFrame):
            # Response already formatted as dataframe
            pass

        else:
            # Response has labeled data (dict)
            data: pd.DataFrame = pd.DataFrame(data).loc[:, self._funding_rate_column_map.keys()]
            data.rename(columns=self._funding_rate_column_map, inplace=True)

        # convert timestamp to datetime
        data.loc[:, FundingRateSchema.timestamp] = data.loc[:, FundingRateSchema.timestamp].apply(
            lambda e: self.ET_to_datetime(e)
        )

        data = data.set_index(FundingRateSchema.timestamp)
        # dropping duplicate timestamp
        # data = data.groupby(FundingRateSchema.timestamp).first()
        # print(1)
        # print(len(data))

        return data

    def ohlcv(
        self,
        instType: Union[InstrumentType, str],
        symbol: Union[Symbol, str],
        interval: Union[Interval, str] = Interval.interval_1d,
        starttime: Union[datetime.datetime, Tuple[int]] = None,  # starttime is the open time of the very first bar
        endtime: Union[
            datetime.datetime, Tuple[int]
        ] = None,  # endtime is the time that occurs immediately after the final close time
        use_cache: bool = True,  # Cache results to prevent repeated requests
        refresh_cache: bool = False,
    ) -> OHLCVFeed:
        """Query Exchange for OHLCV bars

        Args:
            instType (InstrumentType): Instrument Type
            symbol (Symbol): Symbol
            interval (Interval, optional): Bar interval. Defaults to Interval.interval_1d.
            starttime (Union[datetime.datetime, Tuple], optional): Start time. Defaults to listing time.
            endtime (Union[datetime.datetime, Tuple], optional): End time. Defaults to now.
            use_cache (bool): Lookup and/or overwrite cache. If False, request is sent directly to API

        Returns:
            (OHLCVFeed): OHLCV Feed object with columns: [open_time, open, high, low, close, volume]
        """
        instType, symbol, interval, starttime, endtime = self._ohlcv_validate(
            instType, symbol, interval, starttime, endtime
        )
        logger.info("-" * 80)
        logger.info(f"Performing OHLCV for {self.name}: ")
        logger.info(f"instType: {instType.name}")
        logger.info(f"symbol: {symbol.name}")
        logger.info(f"starttime: {starttime}")
        logger.info(f"endtime: {endtime}")
        logger.info("-" * 80)

        # Get actual symbol and interval

        symbol_name = self.get_instrument(instType, symbol)[Instrument.contract_name]
        interval_name, timedelta = self.intervals[interval]  # tuple of (request param, datetime.timedelta)

        df = self._ohlcv(
            instType,
            symbol_name,
            interval_name,
            starttime,
            endtime,
            timedelta,
            strict=True,
            use_cache=use_cache,
            refresh_cache=refresh_cache,
        )

        missing_rows = df.iloc[:, 1].isna().sum()
        if missing_rows > 0:
            logger.info(f"The DataFrame has {missing_rows} missing row(s)")
        logger.info("Done OHLCV Request")

        return OHLCVFeed(df, self.name, self.fee_info, instType, symbol, interval, starttime, endtime)

    def _ohlcv_get_instrument_listing(
        self,
        instType: InstrumentType,
        symbol: Symbol,
        use_cache: bool = True,
        refresh_cache: bool = False,
    ):
        """Return listing for a given instrument"""
        logger.info(f"Getting listing for {self.name}_earliest_{instType.name}_{symbol.name}")

        interval = Interval.interval_1d
        starttime = EARLIEST_OHLCV_DATE
        endtime = datetime.datetime.now()
        symbol_name = self.get_instrument(instType, symbol)[Instrument.contract_name]
        interval_name, timedelta = self.intervals[interval]

        df = self._ohlcv(
            instType,
            symbol_name,
            interval_name,
            starttime,
            endtime,
            timedelta,
            exit_on_first_response=True,
            min_datapoints_required=5,
            strict=False,
            use_cache=False,
        )

        ret_val = df[~df.open.isna()].iloc[0][OHLCVColumn.open_time].to_pydatetime()

        return ret_val


class ExchangeAPIBase(ExchangeBase, AbstractExchangeAPIBase):
    def __init__(self, missing_data_threshold: float = 1, **kwargs):
        self._missing_data_threshold = missing_data_threshold
        rate_limit_delay = 1 / self._max_requests_per_second
        self.dispatcher = Dispatcher(timeout=rate_limit_delay, debug=kwargs.get("debug", False))

        super().__init__(**kwargs)

    # Conversion functions can be overridden in children classes to conform to exchange specific properties
    @staticmethod
    def ET_to_datetime(et):
        """Convert exchange time format to datetime"""
        return datetime.datetime.utcfromtimestamp(int(et) / 1000)

    @staticmethod
    def datetime_to_ET(dt):
        """Convert datetime to exchange time format"""
        return int(dt.replace(tzinfo=datetime.timezone.utc).timestamp() * 1000)

    @staticmethod
    def ET_to_seconds(et):
        """Convert exchange time format to seconds"""
        return int(int(et) / 1000)

    @staticmethod
    def seconds_to_ET(seconds):
        """Convert seconds to exchange time format"""
        return int(seconds * 1000)

    @staticmethod
    def _snap_times(
        a: datetime.datetime, b: datetime.datetime, interval: datetime.timedelta
    ) -> Tuple[datetime.datetime, datetime.datetime]:
        """Snap endpoints a and b

        Args:
            a (datetime.datetime): start time
            b (datetime.datetime): end time
            interval (datetime.timedelta): The time scale to snap times to

        Returns:
            Tuple[datetime.datetime, datetime.datetime]: Returns a new snapped interval of (a, b)
        """
        remainder = (a - datetime.datetime.min) % interval
        if remainder > datetime.timedelta(0):
            starttime = a + (interval - remainder)
        else:
            starttime = a

        remainder = (b - datetime.datetime.min) % interval
        if remainder > datetime.timedelta(0):
            endtime = b - remainder
        else:
            endtime = b

        return starttime, endtime

    def _ohlcv_get_request_intervals(
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
        effective_start_time, effective_end_time = self._snap_times(starttime, endtime, timedelta)

        # Adjust endpoints
        if self._start_inclusive == False:
            # Start time must be immediately before
            effective_start_time -= datetime.timedelta(seconds=1)
        if self._end_inclusive == True:
            # End time must be immediately before
            effective_end_time -= datetime.timedelta(seconds=1)

        cursor = self.datetime_to_ET(effective_start_time)
        startTimes = [cursor]
        endTimes = []
        limits = []
        while cursor < self.datetime_to_ET(effective_end_time):
            cursor += int(limit * self.seconds_to_ET(timedelta.total_seconds()))

            if cursor > self.datetime_to_ET(effective_end_time):
                endTimes.append(self.datetime_to_ET(effective_end_time))
                final_limit = math.ceil(
                    (self.ET_to_datetime(endTimes[-1]) - self.ET_to_datetime(startTimes[-1])) / timedelta
                )
                limits.append(final_limit)
            else:
                endTimes.append(cursor)
                startTimes.append(cursor)
                limits.append(limit)

        logger.debug(f"effective interval: ({effective_start_time}, {effective_end_time}), limits: {limits}")
        return startTimes, endTimes, limits

    @cached("cache/ohlcv", is_method=True, instance_identifier="name")
    def _ohlcv(
        self,
        instType: InstrumentType,
        symbol: str,
        interval: Union[str, int],
        starttime: datetime.datetime,
        endtime: datetime.datetime,
        timedelta: datetime.timedelta,
        exit_on_first_response: bool = False,
        min_datapoints_required: int = 2,
        strict: bool = False,
        use_cache: bool = True,
        refresh_cache: bool = False,
    ) -> pd.DataFrame:
        _requests = []
        limit = self._limit or 100
        start_times, end_times, limits = self._ohlcv_get_request_intervals(starttime, endtime, timedelta, limit)

        for _starttime, _endtime, limit in zip(start_times, end_times, limits):
            request = self._ohlcv_prepare_request(instType, symbol, interval, _starttime, _endtime, limit)
            _requests.append(request)

        expected_datapoints = sum(limits)
        response = []
        for request in _requests:
            res = self.dispatcher.send_request(request)
            res = self._ohlcv_extract_response(res)
            response.extend(res)
            logger.debug(f"Received {len(res)} datapoints")
            logger.debug(f"response head: \n{res[:5]}")
            if len(res) >= min_datapoints_required and exit_on_first_response:
                break

        if len(response) < expected_datapoints:
            if (len(response) / expected_datapoints) > self._missing_data_threshold or len(response) == 0:
                msg = f"Missing {100 * (1 - (len(response) / expected_datapoints))}% of data"
                if strict:
                    raise MissingDataError(msg)
                else:
                    logger.warning(msg)

        df = self._ohlcv_res_to_dataframe(response, starttime, endtime, timedelta)

        return df

    def order_book(
        self,
        symbol: Symbol,
        instType: InstrumentType = InstrumentType.PERPETUAL,
        depth: int = 50,
    ):
        """Return order book snapshot for given instrument"""
        instType, symbol = self._parse_instrument(instType, symbol)
        symbol_name = self.get_instrument(instType, symbol)[Instrument.contract_name]
        if depth is not None:
            order_book_kwargs = {"depth": depth}
        else:
            order_book_kwargs = {}

        request: requests.Request = self._order_book_prepare_request(instType.name, symbol_name, **order_book_kwargs)
        res = self.dispatcher.send_request(request)
        res = self._order_book_extract_response(res)

        res = res.astype({OrderBookSchema.price: float, OrderBookSchema.quantity: float})
        res[OrderBookSchema.quantity] = res[OrderBookSchema.quantity] * self._order_book_quantity_multiplier(
            instType.name, symbol_name
        )
        bids = (
            res[res[OrderBookSchema.side] == OrderBookSide.bid]
            .sort_values(OrderBookSchema.price, ascending=False, ignore_index=True)
            .iloc[:depth]
        )
        asks = (
            res[res[OrderBookSchema.side] == OrderBookSide.ask]
            .sort_values(OrderBookSchema.price, ascending=True, ignore_index=True)
            .iloc[:depth]
        )
        orderbook = pd.concat([bids, asks], ignore_index=True)
        return orderbook

    @cached("cache/hisorical_funding_rate", is_method=True, instance_identifier="name")
    def historical_funding_rate(
        self,
        instType: Union[InstrumentType, str],
        symbol: Union[Symbol, str],
        starttime: datetime.datetime = None,  # .datetime,
        endtime: datetime.datetime = None,  # .datetime,
        timedelta: datetime.timedelta = None,
        limit: int = None,
        use_cache: bool = False,
        refresh_cache: bool = False,
    ) -> pd.DataFrame:
        """Return historical funding rates for given instrument"""

        instType, symbol = self._parse_instrument(instType, symbol)
        # symbol_name = self.get_instrument(instType, symbol)[Instrument.contract_name]
        limit = 50  # self._limit or 100

        interval = Interval.interval_1d
        starttime = EARLIEST_OHLCV_DATE
        endtime = datetime.datetime.now()
        symbol_name = self.get_instrument(instType, symbol)[Instrument.contract_name]
        interval_name, timedelta = self.intervals[interval]
        _requests = []

        # print(symbol)

        start_times, end_times, limits = self._ohlcv_get_request_intervals(starttime, endtime, timedelta, limit)
        for _starttime, _endtime, limit in zip(start_times, end_times, limits):
            # print(symbol_name)
            print((self.ET_to_datetime(_starttime)))
            print(self.ET_to_datetime(_endtime))
            print(_starttime)
            print(_endtime)
            request = self._histrorical_funding_rate_prepare_request(
                instType, symbol_name, _starttime, _endtime, limit
            )
            _requests.append(request)

        response = []
        for request in _requests:
            # print(request)
            res = self.dispatcher.send_request(request)
            res = self._histrorical_funding_rate_extract_response(res)
            print(len(res))
            response.extend(res)
        # logger.debug(f"response head: \n{res[:5]}")

        df_funding = self._funding_rate_res_to_dataframe(response)
        pd.set_option("display.max_rows", 1000)
        print(df_funding)

        # return df_funding
