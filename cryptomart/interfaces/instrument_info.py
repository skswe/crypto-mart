import os
from typing import Callable, Dict

import pandas as pd
from pyutil.cache import cached
from requests import Request

from ..enums import Instrument, Symbol
from ..interfaces.api import APIInterface
from ..types import JSONDataType


class InstrumentInfoInterface(APIInterface):
    """API interface to query instrument information. Columns to be returned are defined in the `Instrument` enum."""

    def __init__(
        self,
        prepare_request: Callable[[str], Request],
        extract_data: Callable[[JSONDataType], pd.DataFrame],
        **api_interface_kwargs
    ):
        """Initialize the interface

        Args:
            prepare_request (Callable[[str], Request]): Function which takes the endpoint URL and returns a `Request` to be sent to the API
            extract_data (Callable[[JSONDataType], pd.DataFrame]): Function which takes the API response and returns a DataFrame with columns
                defined in the `Instrument` enum
        """
        super().__init__(**api_interface_kwargs)
        self.prepare_request = prepare_request
        self.extract_response = extract_data

    def run(self) -> pd.DataFrame:
        """Run main interface function

        Returns:
            pd.DataFrame: Instrument info
        """
        req = self.prepare_request(self.url)
        res = self.dispatcher.send_request(req)
        data = self.extract_response(res)
        return data

    @cached(
        os.path.join(os.getenv("CM_CACHE_PATH", "/tmp/cache"), "symbol_mappings"),
        is_method=True,
        instance_identifiers=["name"],
    )
    def get_symbol_mappings(self) -> Dict[Symbol, str]:
        """Return a dictionary mapping between `Symbol` enum and the instrument ID used by the API

        Returns:
            Dict[Symbol, str]: Mapping of `Symbol` enum to API instrument ID
        """
        instrument_info = self.run()
        return dict(zip(instrument_info[Instrument.cryptomart_symbol], instrument_info[Instrument.exchange_symbol]))
