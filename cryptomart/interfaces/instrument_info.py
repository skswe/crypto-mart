import os
from typing import Callable, Dict, Union

import pandas as pd
from pyutil.cache import cached
from requests import Request

from ..enums import Instrument, Symbol
from ..interfaces.api import APIInterface
from ..types import JSONDataType


class InstrumentInfoInterface(APIInterface):
    """API interface to query instrument information. Columns to be returned are defined in the `Instrument` enum."""

    def __init__(self, **api_interface_kwargs):
        super().__init__(**api_interface_kwargs)

    @cached(
        os.path.join(os.getenv("CM_CACHE_PATH", "/tmp/cache"), "instrument_info"),
        is_method=True,
        instance_identifiers=["name"],
    )
    def run(self, mappings: bool, **cache_kwargs) -> Union[pd.DataFrame, Dict[Symbol, str]]:
        """Run main interface function

        Args:
            mappings (bool): Return Symbol to instrument mappings
        Returns:
            pd.DataFrame: Instrument info or Mapping of `Symbol` enum to API instrument ID
        """
        data = self.execute(self.dispatcher, self.url)

        if mappings:
            return dict(zip(data[Instrument.cryptomart_symbol], data[Instrument.exchange_symbol]))

        return data
