import datetime
import logging

from cryptomart.enums import Symbol

LOGGING_FORMATTER = logging.Formatter("{asctime}.{msecs:03.0f} {levelname:<8} {name:<50}{funcName:>35}:{lineno:<4} {message}", style="{", datefmt="%Y-%m-%d %H:%M:%S")
EARLIEST_OHLCV_DATE = datetime.datetime(2018, 1, 1)
END_OHLCV_DATE = datetime.datetime(2022, 3, 11)
INVALID_DATE = datetime.datetime(1980, 1, 1)
SYMBOL_ALIASES = {
    Symbol.XBT: Symbol.BTC,
}
