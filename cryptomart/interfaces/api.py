import logging

from ..enums import Exchange, InstrumentType, Interface, Symbol
from ..util import Dispatcher


class APIInterface:
    """Base class for unifying an API function across exchanges.
    Organizes loggers by `exchange_name`.`interface_name`.`inst_type` to enable fine-grained control of log messages
    """

    def __init__(
        self,
        exchange_name: Exchange,
        interface_name: Interface,
        inst_type: InstrumentType,
        url: str,
        dispatcher: Dispatcher,
    ):
        """Initialize base class

        Args:
            exchange_name (Exchange): Name of the exchange this interface is for
            interface_name (Interface): Name of the interface
            inst_type (InstrumentType): Type of instrument this interface is for
            url (str): URL of the endpoint to query
            dispatcher (Dispatcher): Dispatcher object to handle http requests for this interface
        """
        self.exchange_name = exchange_name
        self.interface_name = interface_name
        self.inst_type = inst_type
        self.url = url
        self.dispatcher = dispatcher

        self.name = f"{exchange_name}_{interface_name}_{inst_type}"

        self.logger = logging.getLogger(f"cryptomart.{exchange_name}.{interface_name}.{inst_type}")
        self.logger.setLevel("INFO")

    @property
    def log_level(self):
        return self.logger.level

    @log_level.setter
    def log_level(self, level):
        self.logger.setLevel(level)
        self.dispatcher.logger.setLevel(level)
