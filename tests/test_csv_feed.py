import logging
import os

import pytest
from cryptomart.enums import InstrumentType, Interval
from cryptomart.feeds import OHLCVFeed

logger = logging.getLogger(__name__)

DATA_PATH = "tests/data"


@pytest.mark.parametrize("exchange_name", ["CME"])
@pytest.mark.parametrize("symbol", ["BTC", "ETH"])
@pytest.mark.parametrize("inst_type", [InstrumentType.MONTHLY])
@pytest.mark.parametrize("interval", [Interval.interval_1d])
def test_csv_feed(exchange_name: str, symbol: str, inst_type: InstrumentType, interval: Interval):
    feed = OHLCVFeed.from_csv(
        path=os.path.join(DATA_PATH, exchange_name, symbol, inst_type, f"{interval}.csv"),
        exchange_name=exchange_name,
        symbol=symbol,
        inst_type=inst_type,
        interval=interval,
    )
    print(feed)
