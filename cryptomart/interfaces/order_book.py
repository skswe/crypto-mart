from datetime import datetime
from typing import Dict

import pandas as pd

from ..enums import OrderBookSchema, OrderBookSide, Symbol
from ..errors import MissingDataError
from ..interfaces.api import APIInterface


class OrderBookInterface(APIInterface):
    def __init__(
        self,
        instruments: Dict[Symbol, str],
        multipliers: Dict[Symbol, float],
        **api_interface_kwargs,
    ):
        super().__init__(**api_interface_kwargs)
        self.instruments = instruments
        self.multipliers = multipliers

    def run(self, symbol: Symbol, depth: int, **cache_kwargs) -> pd.DataFrame:
        """Run main interface function

        Args:
            symbol (Symbol): Symbol to query
            depth (int): Number of bids/asks to include in the snapshot

        Returns:
            pd.DataFrame: Orderbook
        """
        instrument_id = self.instruments[symbol]
        multiplier = self.multipliers[symbol]
        data = self.execute(self.dispatcher, self.url, instrument_id, depth)
        data[[OrderBookSchema.price, OrderBookSchema.quantity]] = data[
            [OrderBookSchema.price, OrderBookSchema.quantity]
        ].astype(float)

        data[OrderBookSchema.quantity] = data[OrderBookSchema.quantity] * multiplier

        bids = (
            data[data[OrderBookSchema.side] == OrderBookSide.bid]
            .sort_values(OrderBookSchema.price, ascending=False, ignore_index=True)
            .iloc[:depth]
        )
        asks = (
            data[data[OrderBookSchema.side] == OrderBookSide.ask]
            .sort_values(OrderBookSchema.price, ascending=True, ignore_index=True)
            .iloc[:depth]
        )
        orderbook = pd.concat([bids, asks], ignore_index=True)
        return orderbook

    @classmethod
    def data_to_df(cls, res: dict, col_map: dict, split_keys: tuple) -> pd.DataFrame:
        """Format API response to standard dataframe"""
        if split_keys:
            bid_key, ask_key = split_keys
            bids = pd.DataFrame(res[bid_key])
            asks = pd.DataFrame(res[ask_key])
            df = pd.concat(
                [bids, asks], keys=[OrderBookSide.bid, OrderBookSide.ask], names=[OrderBookSchema.side]
            ).reset_index(level=0)
        else:
            df = pd.DataFrame(res)

        if df.empty:
            raise MissingDataError

        df.rename(columns=col_map, inplace=True)
        df[OrderBookSchema.timestamp] = datetime.utcnow().replace(microsecond=0)
        return df[OrderBookSchema._values()]
