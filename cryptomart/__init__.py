import logging

from dotenv import load_dotenv

from . import client, enums, errors, exchanges, feeds, globals, interfaces, types, util
from .client import Client
from .enums import Exchange, InstrumentType, Interval, Symbol
from .exchanges.base import ExchangeAPIBase
from .feeds import OHLCVFeed
from .globals import LOGGING_FORMATTER

load_dotenv()
root_logger = logging.getLogger("cryptomart")
root_logger.setLevel(logging.INFO)
root_logger.addHandler(logging.StreamHandler())
root_logger.handlers[0].setFormatter(LOGGING_FORMATTER)
