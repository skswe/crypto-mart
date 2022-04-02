import functools
import hashlib
import inspect
import logging
import os
import pickle
import sys
import threading
import time
from queue import Queue
from typing import Callable, List, Union

import pandas as pd
import requests

logger = logging.getLogger(__name__)


def stack_dict(d, path=[]) -> list:
    """Return a list, where each element is a list of the dict key path required to reach val, followed by val
    Example:
    >>> stack_dict({'a': {'b': {'c': 1}}, 'd': 2})
    >>> [['a', 'b', 'c', 1], ['d', 2]]

    Args:
        d (dict): The dict to stack

    Returns:
        list: stacked dict
    """
    res = []
    for k, v in d.items():
        if isinstance(v, dict):
            res.extend(stack_dict(v, path + [k]))
        else:
            res.append(path + [k, v])
    return res


def is_sortable(obj):
    try:
        sorted(obj)
        return True
    except TypeError:
        return False


def sort_args(args):
    new_list = []
    for item in args:
        if (isinstance(item, list) or isinstance(item, tuple)) and is_sortable(item):
            new_list.append(sorted(item))
        elif isinstance(item, dict):
            new_list.append(sorted(stack_dict(item)))
        else:
            new_list.append(item)

    return new_list


def sort_kwargs(kwargs):
    return sort_args(stack_dict(kwargs))


class Cache:
    def __init__(self, path: str, name: str, args: str, log_level: str = "INFO"):
        """Creates a cache on disk at the specified `path`. This class acts as
        a wrapper for general request functions to save the result of a request
        to disk for fast lookup later on.

        `active`: If False, all cache queries will return the request function without saving to disk.

        Args:
            path ([str]): Path to store cache on disk
            name ([str]): Name of function or operation being cached
            args ([tuple]): Arguments passed to cached function or operation for logging purposes
        """
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        self.path = path
        self.name = name
        self.args = f"({', '.join(str(arg) for arg in args)})"
        self.active = True
        assert log_level in logging._nameToLevel.keys()
        self.log_level = log_level

    def log(self, *msg):
        logger.log(logging._nameToLevel[self.log_level], *msg)

    def query(
        self,
        key,
        query_fn=None,
        save_fn=pd.to_pickle,
        load_fn=pd.read_pickle,
        query_fn_args=[],
        save_fn_args=[],
        load_fn_args=[],
        query_fn_kwargs={},
        save_fn_kwargs={},
        load_fn_kwargs={},
        active=True,
        refresh=False,
    ):
        if not active:
            return query_fn(*query_fn_args, **query_fn_kwargs)

        if not refresh and self.search(key) is True:
            self.log(f"Using cached value in call to {self.name}{self.args}: {key}")
            return load_fn(os.path.join(self.path, key), *load_fn_args, **load_fn_kwargs)
        else:
            data = query_fn(*query_fn_args, **query_fn_kwargs)
            self.log(f"Saving cached value in call to {self.name}{self.args}: {key}")
            save_fn(data, os.path.join(self.path, key), *save_fn_args, **save_fn_kwargs)
            return data

    def search(self, key):
        return True if key in os.listdir(self.path) else False


def hash_function_args(args, kwargs, additional_args):
    sorted_args = sort_args(args)
    sorted_kwargs = sort_kwargs(kwargs)

    return hashlib.md5(pickle.dumps([sorted_args, sorted_kwargs, additional_args])).hexdigest()


def cached(
    path: str = "cache",
    is_method: bool = False,
    instance_identifier: str = None,
    refresh: bool = False,
    active: bool = True,
    additional_args: list = [],
    log_level: str = "INFO",
):
    """Save the result of the decorated function in a cache. Function arguments are hashed such that subsequent
    calls with the same arguments result in a cache hit

    Args:
        path (str, optional): disk path to store cached objects. Defaults to "cache".
        is_method (bool, optional): whether or not the cached function is an object's method. Defaults to False.
        refresh (bool, optional): whether or not to bypass cache lookup to force a new cache write. Defaults to False.
        active (bool, optional): whether or not to use the cache for the function call. Defaults to True.
        additional_args (list, optional): additional arguments used to identify a unique function call. Defaults to [].
        instance_identifier (str, optional): name of instance attribute to include in hash if `is_method` is `True`. Defaults to "".
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if os.getenv("UNIFIED_DM_DISABLE_CACHE"):
                return func(*args, **kwargs)
            _active = active
            _refresh = refresh
            _additional_args = additional_args
            if is_method:
                # remove self argument
                instance = args[0]
                modified_args = args[1:]
                if instance_identifier:
                    _additional_args = [*additional_args, getattr(instance, instance_identifier)]
            else:
                modified_args = args

            default_kwargs = {
                k: v.default
                for k, v in inspect.signature(func).parameters.items()
                if v.default is not inspect.Parameter.empty
            }
            default_kwargs.update(kwargs)
            kwargs = default_kwargs

            if "refresh_cache" in kwargs:
                _refresh = kwargs["refresh_cache"]
                del kwargs["refresh_cache"]

            if "use_cache" in kwargs:
                _active = kwargs["use_cache"]
                del kwargs["use_cache"]

            key = hash_function_args(modified_args, kwargs, additional_args)
            # logger.debug(f"cache arguments: {modified_args, kwargs, additional_args}")
            # logger.debug(f"cache arguments hash: {key}")
            _func_kwargs = (f"{k}={v}" for k, v in kwargs.items())
            _additional_args_str = (
                (f"additional_args=({', '.join(str(arg) for arg in _additional_args)})",) if _additional_args else ()
            )
            return Cache(
                path,
                func.__name__,
                (
                    *modified_args,
                    *_additional_args_str,
                    *_func_kwargs,
                ),
                log_level=log_level,
            ).query(key, func, query_fn_args=args, query_fn_kwargs=kwargs, refresh=_refresh, active=_active)

        return wrapper

    return decorator


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
    def __init__(self, dispatch_fn: Callable = None, timeout: float = 0, debug: bool = False):
        self.dispatch_fn = dispatch_fn or self._default_dispatch_fn
        self.pending_queue = Queue()
        self.result_queue = Queue()

        self.timeout = timeout

        if debug:
            logger.setLevel("DEBUG")

        # Create daemon to process requests
        worker_thread = threading.Thread(target=self.worker_fn, daemon=True)
        worker_thread.start()

    @staticmethod
    def _default_dispatch_fn(request: requests.Request) -> Union[dict, None]:
        logger.debug(f"Dispatcher: Making request -- {request.method}: {request.url}, params={request.params}")
        try:
            with requests.Session() as s:
                res = s.send(request.prepare()).json()
            assert isinstance(res, dict) or isinstance(res, list), f"Unexpected response: {res}"
        except Exception as e:
            logger.error(f"Dispatcher: Error in request -- {request.method}: {request.url}: {e}")
            res = None
        logger.debug("Dispatcher: Got response")
        return res

    def add_request(self, request: requests.Request):
        """Add single request to the dispatch queue to be dispatched as soon as possible"""
        self.pending_queue.put(request)

    def add_requests(self, requests: List[requests.Request]):
        """Add group of requests to the dispatch queue to be dispatched as soon as possible"""
        for request in requests:
            self.pending_queue.put(request)

    def get_result(self) -> Union[dict, None]:
        """Get the latest result from the dispatcher. Blocks until a result is available"""
        res = self.result_queue.get(block=True)
        self.result_queue.task_done()
        return res

    def send_request(self, request: requests.Request) -> Union[dict, None]:
        """Send and receive a single request"""
        self.add_request(request)
        return self.get_result()

    def send_requests(self, requests: List[requests.Request]) -> List[Union[dict, None]]:
        """Send and receive a group of requests"""
        self.add_requests(requests)
        self.pending_queue.join()
        results = []
        while not self.result_queue.empty():
            results.append(self.get_result())
        return results

    def worker_fn(self):
        logger.debug("Dispatcher: Worker thread starting")
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


def timed(return_time=False):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            ret = func(*args, **kwargs)
            end_time = time.time()
            elapsed_time = end_time - start_time
            logger.info(f"runtime ({func.__name__}): {elapsed_time}s")
            if return_time:
                return ret, elapsed_time
            return ret

        return wrapper

    return decorator


def redirect_stdout(path: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                if os.path.dirname(path):
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                ref = sys.stdout
                sys.stdout = open(path, "w")
                return func(*args, **kwargs)
            finally:
                sys.stdout = ref

        return wrapper

    return decorator
