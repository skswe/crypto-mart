from pyutil.enums import NameEnum


class Instrument(NameEnum):
    cryptomart_symbol = "cryptomart_symbol"
    exchange_symbol = "exchange_symbol"
    orderbook_multi = "orderbook_multi"
    exchange_list_time = "exchange_list_time"


class OHLCVColumn(NameEnum):
    "Column names for OHLCV data feed"

    open_time = "open_time"
    open = "open"
    high = "high"
    low = "low"
    close = "close"
    volume = "volume"


class FundingRateSchema(NameEnum):
    "Column Schema for Funding rate structure"

    timestamp = "timestamp"
    """Timestamp of Funding Rate"""

    funding_rate = "funding_rate"
    """Value of Funding Rate """


class OrderBookSchema(NameEnum):
    "Column Schema for Order Book data structure"

    price = "price"
    """Price of order"""

    quantity = "quantity"
    """Quantity of order"""

    side = "side"
    """See OrderBookSide"""

    timestamp = "timestamp"
    """Timestamp of snapshot"""


class OrderBookSide(NameEnum):
    """Possible values for OrderBookSchema.side"""

    ask = "a"
    bid = "b"


class Exchange(NameEnum):
    """Names of registered exchanges in the API"""

    BINANCE = "binance"
    BITMEX = "bitmex"
    BYBIT = "bybit"
    OKEX = "okex"
    GATEIO = "gateio"
    KUCOIN = "kucoin"


class Interface(NameEnum):
    INSTRUMENT_INFO = "instrument_info"
    OHLCV = "ohlcv"
    FUNDING_RATE = "funding_rate"
    ORDER_BOOK = "order_book"


class InstrumentType(NameEnum):
    """Names of registered instrument types in the API"""

    PERPETUAL = "perpetual"
    PERP = "perpetual"
    QUARTERLY = "quarterly"
    MONTHLY = "monthly"
    SPOT = "spot"


class Interval(NameEnum):
    """Names of registered historical candlestick data intervals in the API"""

    interval_1m = "interval_1m"
    interval_5m = "interval_5m"
    interval_15m = "interval_15m"
    interval_1h = "interval_1h"
    interval_4h = "interval_4h"
    interval_8h = "interval_8h"
    interval_12h = "interval_12h"
    interval_1d = "interval_1d"
    interval_1w = "interval_1w"
