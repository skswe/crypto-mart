import logging
from datetime import datetime

import pytest
from unified_dm.enums import InstrumentType, Interval, Symbol
from unified_dm.exchanges import CME, FTX, Binance, BitMEX, Bybit, CoinFLEX, GateIO, Kucoin, OKEx
from unified_dm.exchanges.bases import ExchangeBase, MissingDataError
from unified_dm.feeds import OHLCVColumn

logger = logging.getLogger(__name__)

# @pytest.fixture(params=[Interval.interval_1d, Interval.interval_12h, Interval.interval_4h, Interval.interval_1h])
@pytest.fixture(params=[Interval.interval_1d])
def interval(request):
    return request.param


@pytest.fixture(params=[Symbol.BTC])
def symbol(request):
    return request.param


@pytest.fixture(params=[InstrumentType.PERPETUAL, InstrumentType.QUARTERLY, InstrumentType.MONTHLY])
def instType(request):
    return request.param


@pytest.fixture
def debug():
    return True


@pytest.fixture(
    params=[
        (datetime(2020, 5, 1), datetime(2020, 6, 1)),
        (datetime(2020, 10, 1), datetime(2020, 11, 1)),
        (datetime(2021, 3, 1), datetime(2021, 4, 1)),
        (datetime(2021, 5, 1), datetime(2021, 6, 1)),
        (datetime(2021, 10, 1), datetime(2021, 11, 1)),
    ]
)
def times(request):
    return request.param


def _check_ohlcv_response(api: ExchangeBase, instType, symbol, times, interval):
    starttime, endtime = times
    if interval not in api.intervals:
        pytest.skip("Exchange does not support this interval")
    if not api.has_instrument(instType, symbol):
        pytest.skip("Exchange does not support this instrument")
    try:
        res = api.ohlcv(instType, symbol, interval, starttime, endtime, use_cache=False)
    except MissingDataError as e:
        pytest.skip(f"Missing data in OHLCV call: {e}")

    expected_datapoints = (endtime - starttime) / api.intervals[interval][1]
    assert len(res) == expected_datapoints, "Unexpected number of datapoints returned"
    assert res.iloc[0][OHLCVColumn.open_time] == starttime, "Unexpected start time received"
    logger.info(f"Missing {sum(res.open.isna())} values")


def test_binance_ohlcv(instType, symbol, interval, times, debug):
    api = Binance(debug)
    _check_ohlcv_response(api, instType, symbol, times, interval)


def test_bybit_ohlcv(instType, symbol, interval, times, debug):
    api = Bybit(debug)
    _check_ohlcv_response(api, instType, symbol, times, interval)


def test_ftx_ohlcv(instType, symbol, interval, times, debug):
    api = FTX(debug)
    _check_ohlcv_response(api, instType, symbol, times, interval)


def test_okex_ohlcv(instType, symbol, interval, times, debug):
    api = OKEx(debug)
    _check_ohlcv_response(api, instType, symbol, times, interval)


def test_coinflex_ohlcv(instType, symbol, interval, times, debug):
    api = CoinFLEX(debug)
    _check_ohlcv_response(api, instType, symbol, times, interval)


def test_kucoin_ohlcv(instType, symbol, interval, times, debug):
    api = Kucoin(debug)
    _check_ohlcv_response(api, instType, symbol, times, interval)


def test_gateio_ohlcv(instType, symbol, interval, times, debug):
    api = GateIO(debug)
    _check_ohlcv_response(api, instType, symbol, times, interval)


def test_bitmex_ohlcv(instType, symbol, interval, times, debug):
    api = BitMEX(debug)
    _check_ohlcv_response(api, instType, symbol, times, interval)


def test_cme_ohlcv(instType, symbol, interval, times, debug):
    api = CME(debug)
    _check_ohlcv_response(api, instType, symbol, times, interval)
