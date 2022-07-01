import datetime
import logging
import math
import threading
import time
from queue import Queue
from typing import Callable, List, Tuple, Union

import pandas as pd
import requests

from .types import JSONDataType, TimeType


def int_to_dt(time: int) -> datetime.datetime:
    """Convert milliseconds, seconds, microseconds to datetime"""
    for denominator in [1, 1e3, 1e6]:
        try:
            return datetime.datetime.utcfromtimestamp(time / denominator).replace(tzinfo=None, microsecond=0)
        except (ValueError, AttributeError):
            continue


def parse_time(time: TimeType) -> datetime.datetime:
    """Convert TimeType to datetime"""
    if isinstance(time, pd.Timestamp):
        return time.to_pydatetime().replace(tzinfo=None, microsecond=0)
    elif isinstance(time, int) or isinstance(time, float):
        return int_to_dt(time)
    elif isinstance(time, datetime.datetime):
        return time.replace(tzinfo=None, microsecond=0)
    elif isinstance(time, tuple):
        return datetime.datetime(*time, tzinfo=None)
    elif isinstance(time, str):
        try:
            # time is an string literal integer
            time = int(time)  # raises ValueError if it cant convert to int
            return int_to_dt(time)
        except ValueError:
            # time is a string time format
            return pd.to_datetime(time).to_pydatetime().replace(tzinfo=None, microsecond=0)


def dt_to_timestamp(dt: datetime.datetime, string=False, granularity="seconds") -> Union[str, int]:
    """Convert datetime to either string or integer timestamp"""
    if granularity == "seconds":
        coeff = 1
    elif granularity == "milliseconds":
        coeff = 1000
    else:
        raise ValueError(f"Invalid granularity provided: {granularity}")

    if string:
        return dt.replace(tzinfo=datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    else:
        return int(dt.replace(tzinfo=datetime.timezone.utc).timestamp() * coeff)


def show_df(df, max_rows=None, max_columns=None, width=1000):
    """Display a pandas DataFrame without truncating"""
    with pd.option_context(
        "display.max_rows", max_columns, "display.max_columns", max_columns, "display.width", width
    ):
        print(df)


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


def get_request_intervals(
    starttime: datetime.datetime,
    endtime: datetime.datetime,
    timedelta: datetime.timedelta,
    limit: int,
) -> Tuple[List[int], List[datetime.datetime], List[datetime.datetime]]:
    """Partition a time period into chunks of `timedelta * limit`

    Returns:
        Tuple[List[datetime.datetime], List[datetime.datetime], List[int]]: The starttime, endtime, count(timedelta) of each partition
    """
    TIME_BUFFER = {"seconds": 1}

    effective_start_time, effective_end_time = snap_times(starttime, endtime, timedelta)
    effective_start_time -= datetime.timedelta(**TIME_BUFFER)
    effective_end_time += datetime.timedelta(**TIME_BUFFER)

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

    return start_times, end_times, limits


class Clock:
    def __init__(self, intitial_time: float = 0):
        self.last_checkpoint = time.time() - intitial_time

    def lap(self):
        _time = self.time()
        self.last_checkpoint = time.time()
        return _time

    def start(self):
        self.last_checkpoint = time.time()

    def time(self):
        return time.time() - self.last_checkpoint


class Dispatcher:
    def __init__(self, name: str, dispatch_fn: Callable = None, timeout: float = 0, pre_request_hook=None):
        self.dispatch_fn = dispatch_fn or self._default_dispatch_fn
        self.pre_request_hook = pre_request_hook or (lambda r: r)
        self.pending_queue = Queue()
        self.result_queue = Queue()

        self.timeout = timeout

        self.logger = logging.getLogger(f"cryptomart.{name}")

        # Create daemon to process requests
        worker_thread = threading.Thread(target=self.worker_fn, daemon=True)
        worker_thread.start()

    def _default_dispatch_fn(self, request: requests.Request) -> Union[JSONDataType, None]:
        self.logger.debug(f"Dispatcher: Making request -- {request.method}: {request.url}, params={request.params}")
        try:
            with requests.Session() as s:
                res = s.send(self.pre_request_hook(request.prepare())).json()
            assert isinstance(res, dict) or isinstance(res, list), f"Unexpected response: {res}"
        except Exception as e:
            self.logger.error(f"Dispatcher: Error in request -- {request.method}: {request.url}: {e}", exc_info=True)
            res = None
        self.logger.debug("Dispatcher: Got response")
        return res

    def add_request(self, request: requests.Request):
        """Add single request to the dispatch queue to be dispatched as soon as possible"""
        self.pending_queue.put(request)

    def add_requests(self, requests: List[requests.Request]):
        """Add group of requests to the dispatch queue to be dispatched as soon as possible"""
        for request in requests:
            self.pending_queue.put(request)

    def get_result(self) -> Union[JSONDataType, None]:
        """Get the latest result from the dispatcher. Blocks until a result is available"""
        res = self.result_queue.get(block=True)
        self.result_queue.task_done()
        return res

    def send_request(self, request: requests.Request) -> Union[JSONDataType, None]:
        """Send and receive a single request"""
        self.add_request(request)
        return self.get_result()

    def send_requests(self, requests: List[requests.Request]) -> List[Union[JSONDataType, None]]:
        """Send and receive a group of requests"""
        self.add_requests(requests)
        self.pending_queue.join()
        results = []
        while not self.result_queue.empty():
            results.append(self.get_result())
        return results

    def worker_fn(self):
        self.logger.debug("Worker thread starting")
        time_since_request = Clock(intitial_time=self.timeout)
        while True:
            time_to_wait = self.timeout - time_since_request.time()
            if time_to_wait > 0:
                time.sleep(time_to_wait)

            request = self.pending_queue.get(block=True)
            time_since_request.lap()
            result = self.dispatch_fn(request)
            self.result_queue.put(result)
            self.pending_queue.task_done()
