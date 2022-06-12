import os
from typing import Dict, Union

import numpy as np
import pandas as pd
from cryptomart.errors import MissingDataError
from cryptomart.util import parse_time
from pyutil.cache import cached

from ..enums import Instrument, Symbol
from ..globals import SYMBOL_ALIASES
from ..interfaces.api import APIInterface


class InstrumentInfoInterface(APIInterface):
    """API interface to query instrument information. Columns to be returned are defined in the `Instrument` enum."""

    def __init__(self, **api_interface_kwargs):
        super().__init__(**api_interface_kwargs)

    @cached(
        os.path.join(os.getenv("CM_CACHE_PATH", "/tmp/cache"), "instrument_info"),
        is_method=True,
        instance_identifiers=["name"],
    )
    def run(self, map_column: str, **cache_kwargs) -> Union[pd.DataFrame, Dict[Symbol, str]]:
        """Run main interface function

        Args:
            map_column (str): If provided, returns a dict of Symbol -> map_column
        Returns:
            pd.DataFrame: Instrument info or Mapping of `Symbol` enum to API instrument ID
        """
        data = self.execute(self.dispatcher, self.url)
        data[Instrument.cryptomart_symbol].replace(SYMBOL_ALIASES, inplace=True)

        for col in Instrument._values():
            if col not in data:
                data[col] = np.nan

        data.loc[data[Instrument.exchange_list_time].notna(), Instrument.exchange_list_time] = data.loc[
            data[Instrument.exchange_list_time].notna(), Instrument.exchange_list_time
        ].apply(lambda e: parse_time(e))

        data[Instrument.orderbook_multi] = data[Instrument.orderbook_multi].fillna(1).astype(float)

        if map_column:
            return dict(zip(data[Instrument.cryptomart_symbol], data[map_column]))

        return data

    @classmethod
    def data_to_df(cls, data: dict, col_map: dict) -> pd.DataFrame:
        """Format API response to standard dataframe"""
        df = pd.DataFrame(data)
        if df.empty:
            raise MissingDataError
        df = pd.concat([df, df.rename(columns=col_map)[col_map.values()]], axis=1)
        return df
