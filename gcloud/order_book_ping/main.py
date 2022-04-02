import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor

from numpy import isin
from pandas import DataFrame

# Since GOOGLE_FUNCTION_SOURCE is modified, the directory of this file will be in sys.path rather than the root workspace directory
# Insert root directory of build location (/workspace) to sys.path
sys.path.append(os.getcwd())
import unified_dm

N_WORKERS = 5
ORDER_BOOK_DEPTH = 20
ORDER_BOOK_SHAPE = (ORDER_BOOK_DEPTH * 2, len(unified_dm.enums.OrderBookSchema))
SKIP_SYMBOLS = []
SKIP_EXCHANGES = {unified_dm.Exchange.CME}


def order_book_ping(request):
    dm = unified_dm.DataMart(debug=False)
    logger = logging.getLogger("unified_dm")
    errors = []

    def get_order_book(id, exchange, symbol, instType):
        try:
            logger.info(f"Getting order book: #{id:<4} {exchange.name:<15} {symbol.name:<15} {instType.name}")

            order_book = dm.exchange_instance_map[exchange].order_book(symbol, instType, depth=ORDER_BOOK_DEPTH)
            if isinstance(order_book, DataFrame) and order_book.shape == ORDER_BOOK_SHAPE:
                logger.info(
                    f"Order book received: #{id:<4} {exchange.name:<15} {symbol.name:<15} {instType.name} ... Pushing to database"
                )
                # Push to database
                pass
        except Exception as e:
            errors.append((exchange, symbol, instType, e))

    def get_all_instruments(exchanges=unified_dm.Exchange.members() - SKIP_EXCHANGES):
        exchange_symbols = dict()
        symbols = []
        for exchange in exchanges:
            exchange_inst = dm.exchange_instance_map[exchange]
            perpetual_instruments = exchange_inst.active_instruments[
                exchange_inst.active_instruments.instType == unified_dm.InstrumentType.PERPETUAL
            ]
            filtered_symbols = perpetual_instruments[~isin(perpetual_instruments.symbol, SKIP_SYMBOLS)]
            exchange_symbols[exchange] = list(
                zip(filtered_symbols.symbol.to_list(), filtered_symbols.instType.to_list())
            )

        exchange_pointer = 0
        while len(exchange_symbols.keys()) > 0:
            exchange = list(exchange_symbols.keys())[exchange_pointer % len(exchange_symbols.keys())]
            try:
                symbol = exchange_symbols[exchange].pop()
                symbols.append((exchange_pointer, exchange, *symbol))
            except IndexError:
                exchange_symbols.pop(exchange)
            exchange_pointer += 1

        logger.info(f"Total symbols to query: {len(symbols)}")
        return symbols

    @unified_dm.util.timed()
    def run_main_script():
        with ThreadPoolExecutor(max_workers=N_WORKERS) as executor:
            executor.map(lambda args: get_order_book(*args), get_all_instruments())

    run_main_script()

    logger.info("Order book completed")
    logger.info("Exceptions thrown by worker threads: ")
    for error in errors:
        logger.warning(error)

    if len(errors) == 0:
        return "Success"
    else:
        return "Some threads raised exceptions. See cloud logs for more details."
