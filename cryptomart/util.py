import datetime
import logging
import threading
import time
from queue import Queue
from typing import Callable, List, Union

import requests

from .types import TimeType


def parse_time(time: TimeType) -> datetime.datetime:
    if isinstance(time, datetime.datetime):
        return time
    elif isinstance(time, int) or isinstance(time, float):
        for denominator in [1, 1e3, 1e6]:
            try:
                return datetime.datetime.utcfromtimestamp(time / denominator)
            except AttributeError:
                continue
    elif isinstance(time, str):
        return datetime.datetime(time)
    elif isinstance(time, tuple):
        return datetime.datetime(*time)


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
    def __init__(self, name: str, dispatch_fn: Callable = None, timeout: float = 0):
        self.dispatch_fn = dispatch_fn or self._default_dispatch_fn
        self.pending_queue = Queue()
        self.result_queue = Queue()

        self.timeout = timeout

        self.logger = logging.getLogger(f"cryptomart.{name}")

        # Create daemon to process requests
        worker_thread = threading.Thread(target=self.worker_fn, daemon=True)
        worker_thread.start()

    def _default_dispatch_fn(self, request: requests.Request) -> Union[dict, None]:
        self.logger.debug(f"Dispatcher: Making request -- {request.method}: {request.url}, params={request.params}")
        try:
            with requests.Session() as s:
                res = s.send(request.prepare()).json()
            assert isinstance(res, dict) or isinstance(res, list), f"Unexpected response: {res}"
        except Exception as e:
            self.logger.error(f"Dispatcher: Error in request -- {request.method}: {request.url}: {e}")
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
