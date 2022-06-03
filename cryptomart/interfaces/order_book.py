from typing import Callable, Dict

import pandas as pd

from ..enums import OrderBookSchema, OrderBookSide, Symbol
from ..interfaces.api import APIInterface
from ..util import Dispatcher


def default_get_multiplier(dispatcher: Dispatcher, instrument_id: str, **cache_kwargs):
    return 1


class OrderBookInterface(APIInterface):
    def __init__(
        self,
        instruments: Dict[Symbol, str],
        get_multiplier: Callable[[Dispatcher, str], float] = default_get_multiplier,
        **api_interface_kwargs,
    ):
        self.instruments = instruments
        self.get_multiplier = get_multiplier
        super().__init__(**api_interface_kwargs)

    def run(self, symbol: Symbol, depth: int = 20, **cache_kwargs) -> pd.DataFrame:
        instrument_id = self.instruments[symbol]
        data = self.execute(self.dispatcher, self.url, instrument_id, depth)

        data = data.astype({OrderBookSchema.price: float, OrderBookSchema.quantity: float})
        data[OrderBookSchema.quantity] = data[OrderBookSchema.quantity] * self.get_multiplier(
            self.dispatcher,
            instrument_id,
            cache_kwargs=cache_kwargs,
        )

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
