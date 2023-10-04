import datetime
import functools
import hashlib
import inspect
import logging
import math
import os
import pickle
import threading
import time
from queue import Queue
from typing import Callable, List, Tuple, Union

import pandas as pd
import requests

from .types import JSONDataType, TimeType

logger = logging.getLogger(__name__)


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
    elif isinstance(time, datetime.date):
        try:
            return time.replace(tzinfo=None, microsecond=0)
        except TypeError:
            # time is a date
            return datetime.datetime(time.year, time.month, time.day)
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
    def __init__(
        self,
        name: str,
        dispatch_fn: Callable = None,
        timeout: float = 0,
        pre_request_hook=None,
        limit_exceeded_delay: int = 10,
    ):
        self.dispatch_fn = dispatch_fn or self._default_dispatch_fn
        self.pre_request_hook = pre_request_hook or (lambda r: r)
        self.pending_queue = Queue()
        self.result_queue = Queue()

        self.timeout = timeout
        self.limit_exceeded_delay = limit_exceeded_delay

        self.logger = logging.getLogger(f"cryptomart.{name}")

        # Create daemon to process requests
        worker_thread = threading.Thread(target=self.worker_fn, daemon=True)
        worker_thread.start()

    def _default_dispatch_fn(self, request: requests.Request) -> Union[JSONDataType, None]:
        self.logger.debug(f"Dispatcher: Making request -- {request.method}: {request.url}, params={request.params}")
        retry = True
        while retry:
            try:
                with requests.Session() as s:
                    res = s.send(self.pre_request_hook(request.prepare()))
                    if res.status_code == 429:
                        self.logger.debug(f"Status 429 received, sleeping for {self.limit_exceeded_delay} seconds...")
                        time.sleep(self.limit_exceeded_delay)
                        continue
                    res = res.json()
                    retry = False
                    assert isinstance(res, dict) or isinstance(res, list), f"Unexpected response: {res}"
            except Exception as e:
                self.logger.error(
                    f"Dispatcher: Error in request -- {request.method}: {request.url}: {e}", exc_info=True
                )
                retry = False
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


class cached:
    @classmethod
    def _sort_dict(cls, d, reverse=False) -> dict:
        """Sort a dict based on keys recursively"""
        new_d = {}
        sorted_keys = sorted(d, reverse=reverse)
        for key in sorted_keys:
            if isinstance(d[key], dict):
                new_d[key] = cls._sort_dict(d[key])
            else:
                new_d[key] = d[key]
        return new_d

    @classmethod
    def _hash_dict(cls, d: dict) -> str:
        """Hash dict in order-agnostic manner by ordering keys and hashes of values"""

        # order keys and hash result
        key_hash = cls._hash_item(list(sorted(d.keys())))

        # hash_item will call this function recursively if dict is passed
        values = [cls._hash_item(i) for i in d.values()]

        return cls._hash_item([key_hash, sorted(values)])

    @classmethod
    def _hash_item(cls, i):
        """Hash a python object by pickling and then applying MD5 to resulting bytes"""
        if isinstance(i, dict):
            return cls._hash_dict(i)
        try:
            hash = hashlib.md5(pickle.dumps(i)).hexdigest()
        except TypeError:
            logger.warning(f"Unable to hash {i}, using hash of the object's class instead")
            hash = hashlib.md5(pickle.dumps(i.__class__)).hexdigest()
        except AttributeError:
            logger.warning(f"Unable to hash the objects class, using hash of class name instead")
            hash = hashlib.md5(pickle.dumps(i.__class__.__name__)).hexdigest()
        return hash

    @classmethod
    def log(cls, level, *msg):
        logger.log(logging._nameToLevel[level], *msg)

    @staticmethod
    def search(path, key):
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        return True if key in os.listdir(path) else False

    def __init__(
        self,
        path: str = "/tmp/cache",
        disabled: bool = False,
        refresh: bool = False,
        log_level: str = "INFO",
        identifiers: list = [],
        path_seperators: list = [],
        instance_identifiers: list = [],
        instance_path_seperators: list = [],
        load_fn=pd.read_pickle,
        save_fn=pd.to_pickle,
        search_fn=None,
        propagate_kwargs: bool = False,
        name: str = None,
    ):
        """Save the result of the decorated function in a cache. Function arguments are hashed such that subsequent
        calls with the same arguments result in a cache hit

        Args:
            path: disk path to store cached objects. Defaults to "cache".
            disabled: whether or not to bypass the cache for the function call. Defaults to False.
            refresh: whether or not to bypass cache lookup to force a new cache write. Defaults to False.
            log_level: level to emit logs at. defaults to INFO
            identifiers: additional arguments that are hashed to identify a unique function call. Defaults to [].
            path_seperators: list of argument names to use as path seperators after `path`
            instance_identifiers: name of instance attributes to include in `identifiers` if `is_method` is `True`. Defaults to [].
            instance_path_seperators: name of instance attributes to include in `path_seperators` if `is_method` is `True`. Defaults to [].
            load_fn: Function to load cached data. Defaults to pd.read_pickle.
            save_fn: Function to save cached data. Defaults to pd.to_pickle.
            search_fn: Function ((path, key) -> bool) to override default search function. Defaults to os.listdir.
            propagate_kwargs: whether or not to propagate keyword arguments to the decorated function. Defaults to False.
            name: name of function or operation being cached. Defaults to None.
        """
        self.params = {
            "path": path,
            "disabled": disabled,
            "refresh": refresh,
            "log_level": log_level,
            "identifiers": identifiers.copy(),
            "path_seperators": path_seperators.copy(),
            "instance_identifiers": instance_identifiers.copy(),
            "instance_path_seperators": instance_path_seperators.copy(),
            "load_fn": load_fn,
            "save_fn": save_fn,
            "search_fn": search_fn or self.search,
            "propagate_kwargs": propagate_kwargs,
            "name": name,
        }

    def __call__(self, func):
        self.params["name"] = self.params["name"] or func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            all_args = self._sort_dict(inspect.getcallargs(func, *args, **kwargs))

            # Update params using override passed in through calling function
            params = self.get_cache_params(kwargs)
            return self.perf_cache_lookup(func, params, all_args, *args, **kwargs)

        return wrapper

    def get_cache_params(self, kwargs):
        params = {}
        for k, v in self.params.items():
            if isinstance(v, list) or isinstance(v, dict):
                params[k] = v.copy()
            else:
                params[k] = v

        if "cache_kwargs" in kwargs:
            # Support special cache_kwargs parameter in case calling function has a name clash with cache params
            params.update(kwargs["cache_kwargs"])
            if not params["propagate_kwargs"]:
                del kwargs["cache_kwargs"]

        else:
            # Since cache_kwargs was not provided, check for overrides directly in kwargs.
            # Note that params get deleted from kwargs so cache_kwargs should be used in case of
            # name conflicts
            params.update(kwargs)

            if not params["propagate_kwargs"]:
                for key in params.keys():
                    try:
                        # Delete override from function kwargs before passing to query
                        del kwargs[key]
                    except KeyError:
                        pass
        return params

    @classmethod
    def perf_cache_lookup(cls, func, params, all_args, *args, **kwargs):
        path = params["path"]
        disabled = params["disabled"]
        refresh = params["refresh"]
        log_level = params["log_level"]
        identifiers = params["identifiers"]
        path_seperators = params["path_seperators"]
        instance_identifiers = params["instance_identifiers"]
        instance_path_seperators = params["instance_path_seperators"]
        load_fn = params["load_fn"]
        save_fn = params["save_fn"]
        search_fn = params["search_fn"]
        name = params["name"]

        # Short circuit if disabled
        if disabled:
            return func(*args, **kwargs)

        # Parse identifiers and path seperators
        path_seperators = [all_args[ps] for ps in path_seperators]
        if "self" in all_args:
            instance = all_args["self"]
            identifiers.extend([getattr(instance, id) for id in instance_identifiers])
            path_seperators.extend([getattr(instance, ps) for ps in instance_path_seperators])

        # Add path seperators
        path = os.path.join(path, *path_seperators)

        # Hash arguments
        hashable = {k: v for k, v in all_args.items() if k not in params and k not in ["cache_kwargs", "self"]}
        key = cls._hash_item([cls._hash_item(i) for i in [hashable, sorted(identifiers)]])

        # Logs will show identifiers and hashable arguments in the function call
        argument_string = (*(f"(id:{i})" for i in identifiers), *(f"{k}={v}" for k, v in hashable.items()))
        argument_string = f"({', '.join(str(arg) for arg in argument_string)})"

        # Cache lookup
        if not refresh and search_fn(path, key) is True:
            cls.log(log_level, f"Using cached value in call to {name}{argument_string} | key={key} ({path})")
            return load_fn(os.path.join(path, key))
        else:
            data = func(*args, **kwargs)
            cls.log(log_level, f"Saving cached value in call to {name}{argument_string} | key={key} ({path})")
            save_fn(data, os.path.join(path, key))
            return data


# Forward Definition
class NameEnum:
    ...


class RemovedAttribute:
    def __get__(self, instance, owner):
        raise AttributeError


class NameEnumMeta(type):
    def __len__(self):
        return len(set(self._values()))

    def __iter__(self):
        return set(self._values()).__iter__()

    def __delattr__(self, __name: str) -> None:
        if hasattr(self, __name) and __name in self.__fields__:
            del self.__fields__[__name]
            setattr(self, __name, RemovedAttribute())
        else:
            super().__delattr__(__name)

    def __init__(self, name, bases, dict):
        if len(bases) > 0 and issubclass(bases[0], NameEnum) and bases[0].__name__ != "NameEnum":
            parent_fields = bases[0].__fields__
            for k, v in parent_fields.items():
                setattr(self, k, v)
        else:
            parent_fields = {}

        self.__reserved_fields__ = ["_names", "_values", "_reverse_lookup"]
        self.__fields__ = parent_fields
        for k in dict.keys():
            if not k.startswith("__") and k not in self.__reserved_fields__:
                self.__fields__[k] = dict[k]

        super().__init__(name, bases, dict)


class NameEnum(str, metaclass=NameEnumMeta):
    """Base class for simple plain class string enums"""

    @classmethod
    def _names(cls):
        return list(cls.__fields__.keys())

    @classmethod
    def _values(cls):
        return list(set(cls.__fields__.values()))

    @classmethod
    def _reverse_lookup(cls, value):
        for k, v in cls.__fields__.items():
            if v == value:
                return k
        raise ValueError(f"{value} not in {cls.__name__}")
