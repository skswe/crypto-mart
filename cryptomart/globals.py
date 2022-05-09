import datetime
import logging

from cryptomart.enums import Symbol

LOGGING_FORMATTER = logging.Formatter("{levelname:<8} {name:>30}{funcName:>35}:{lineno:<4} {message}", style="{")
EARLIEST_OHLCV_DATE = datetime.datetime(2018, 1, 1)
END_OHLCV_DATE = datetime.datetime(2022, 3, 11)
INVALID_DATE = datetime.datetime(1980, 1, 1)
