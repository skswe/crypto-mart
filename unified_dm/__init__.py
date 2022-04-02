import logging

from .dm import DataMart, get_spread
from .enums import Exchange, InstrumentType, Interval, Symbol
from .exchanges.bases import FeeInfo
from .feeds import OHLCVFeed, Spread
from .globals import LOGGING_FORMATTER

root_logger = logging.getLogger("unified_dm")
root_logger.setLevel(logging.INFO)
root_logger.addHandler(logging.StreamHandler())
root_logger.handlers[0].setFormatter(LOGGING_FORMATTER)
