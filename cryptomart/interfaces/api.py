import logging
from typing import Any, Callable, Dict, List, Union

import pandas as pd

from ..enums import InstrumentType, Interface
from ..errors import APIError, MissingDataError
from ..exchanges.base import ExchangeAPIBase
from ..types import JSONDataType
from ..util import Dispatcher


class APIInterface:
    """Base class for unifying an API function across exchanges.
    Organizes loggers by `exchange_name`.`interface_name`.`inst_type` to enable fine-grained control of log messages
    """

    def __init__(
        self,
        exchange: ExchangeAPIBase,
        interface_name: Interface,
        inst_type: InstrumentType,
        url: str,
        dispatcher: Dispatcher,
        execute: Callable[[Dispatcher, str, Any], Any],
    ):
        """Initialize base class

        Args:
            exchange_name (Exchange): Name of the exchange this interface is for
            interface_name (Interface): Name of the interface
            inst_type (InstrumentType): Type of instrument this interface is for
            url (str): URL of the endpoint to query
            dispatcher (Dispatcher): Dispatcher object to handle http requests for this interface
        """
        self.exchange = exchange
        self.exchange_name = exchange.name
        self.interface_name = interface_name
        self.inst_type = inst_type
        self.url = url
        self.dispatcher = dispatcher
        self.execute = execute

        self.name = f"{exchange.name}_{interface_name}_{inst_type}"

        self.logger = logging.getLogger(f"cryptomart.{exchange.name}.{interface_name}.{inst_type}")
        self.logger.debug(f"Initializing {inst_type} {interface_name} interface")

    @property
    def log_level(self):
        return self.logger.level

    @log_level.setter
    def log_level(self, level):
        self.logger.setLevel(level)
        self.dispatcher.logger.setLevel(level)

    @classmethod
    def extract_response_data(
        cls,
        response: JSONDataType,
        data_attrs: List[str],
        code_attrs: List[str],
        expected_code: Union[str, int, None],
        err_msg_attrs: List[str],
        *args,
        raw: bool = False,
    ) -> Any:
        """Check JSON response object for errors and return data portion of response or error message.

        Args:
            response (JSONDataType): Response object
            data_attrs (List[str]): List of dict keys to index the data that needs to be extracted from the response object. Empty list if no indexing required.
            code_attrs (List[str]): List of dict keys to index the response code to be compared with `expected_code`. Empty list of no response code available.
            expected_code (Union[str, int]): Expected response code. `None` if no response code available.
            err_msg_attrs (List[str]): List of dict keys to index an error message from the response object. Empty list of no error message available.
            *args: Arguments passed to cls.data_to_df.
            raw (bool): If True, skips application of cls.data_to_df() to response. Default is False.

        Raises:
            APIError: When the response contains an invalid response code.
            MissingDataError: Data is missing in the response.

        Returns:
            JSONDataType: extracted JSON data
        """

        if code_attrs:
            # Check for provided code response
            code_response = response
            for attr in code_attrs:
                code_response = code_response[attr]

            # Check code response matches expected value
            if code_response != expected_code:
                # Read error message
                err_response = response
                for attr in err_msg_attrs:
                    err_response = err_response[attr]
                raise APIError(err_response)

        data_response = response
        for attr in data_attrs:
            data_response = data_response[attr]
        try:
            if raw:
                return data_response
            else:
                return cls.data_to_df(data_response, *args)
        except Exception as e:
            # Try to extract error message when unexpected error occurs. else just raise the error
            try:
                err_response = response
                for attr in err_msg_attrs:
                    err_response = err_response[attr]
                if isinstance(err_response, str):
                    raise APIError(err_response)
                raise e
            except:
                raise e

    @classmethod
    def data_to_df(cls, res: JSONDataType, col_map: dict) -> pd.DataFrame:
        """Default method to format API response to standard dataframe"""
        df = pd.DataFrame(res)
        if df.empty:
            raise MissingDataError
        df.rename(columns=col_map, inplace=True)
        return df[col_map.values()]
