import pytest
import unified_dm
from unified_dm.enums import OrderBookSchema, OrderBookSide

dm = unified_dm.DataMart()


def test_order_book():
    for exchange, exchange_obj in dm.exchange_instance_map.items():
        if isinstance(exchange_obj, unified_dm.exchanges.bases.ExchangeAPIBase):
            print(exchange)
            orderbook = exchange_obj.order_book("BTC")
            assert (orderbook.columns == OrderBookSchema.names()).all()

            bids = orderbook[orderbook[OrderBookSchema.side] == OrderBookSide.bid].reset_index(drop=True)
            asks = orderbook[orderbook[OrderBookSchema.side] == OrderBookSide.ask].reset_index(drop=True)

            correct_bids = bids.sort_values(OrderBookSchema.price, ascending=False, ignore_index=True)
            correct_asks = asks.sort_values(OrderBookSchema.price, ascending=True, ignore_index=True)

            assert (bids == correct_bids).all(axis=None)
            assert (asks == correct_asks).all(axis=None)
