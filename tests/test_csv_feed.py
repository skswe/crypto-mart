import logging
import os

import pytest
from cryptomart.enums import InstrumentType, Interval, Symbol
from cryptomart.feeds import CSVFeed

logger = logging.getLogger(__name__)

DATA_PATH = "tests/data"


@pytest.mark.parametrize("exchange_name", ["CME"])
@pytest.mark.parametrize("symbol", [Symbol.BTC, Symbol.ETH])
@pytest.mark.parametrize("instType", [InstrumentType.MONTHLY])
@pytest.mark.parametrize("interval", [Interval.interval_1d])
def test_csv_feed(exchange_name: str, symbol: Symbol, instType: InstrumentType, interval: Interval):
    feed = CSVFeed(
        path=os.path.join(DATA_PATH, exchange_name, symbol, instType, f"{interval}.csv"),
        exchange_name=exchange_name,
        symbol=symbol,
        instType=instType,
        interval=interval,
    )
    print(feed)