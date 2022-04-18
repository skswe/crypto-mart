import logging

from .client import Client
from .enums import Exchange, InstrumentType, Interval, Symbol
from .feeds import OHLCVFeed
from .globals import LOGGING_FORMATTER

root_logger = logging.getLogger("cryptomart")
root_logger.setLevel(logging.INFO)
root_logger.addHandler(logging.StreamHandler())
root_logger.handlers[0].setFormatter(LOGGING_FORMATTER)
