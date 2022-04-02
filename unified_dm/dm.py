"""Main API"""

import logging
import os
from datetime import datetime
from itertools import combinations
from typing import Dict, List, Union

import numpy as np
import pandas as pd

from .enums import Exchange, InstrumentType, Interval, Symbol
from .exchanges import CME, FTX, Binance, BitMEX, Bybit, CoinFLEX, GateIO, Kucoin, OKEx
from .exchanges.bases import ExchangeBase, MissingDataError
from .feeds import Spread
from .globals import LOGGING_FORMATTER
from .util import cached

EXCHANGE_CLASS_MAP: Dict[Exchange, ExchangeBase] = {
    Exchange.BINANCE: Binance,
    Exchange.BYBIT: Bybit,
    Exchange.BITMEX: BitMEX,
    Exchange.CME: CME,
    Exchange.COINFLEX: CoinFLEX,
    Exchange.FTX: FTX,
    Exchange.GATEIO: GateIO,
    Exchange.KUCOIN: Kucoin,
    Exchange.OKEX: OKEx,
}

logger = logging.getLogger(__name__)


def get_spread(exchange_a: str, exchange_b: str, symbol: str, instType: str = "PERPETUAL", **kwargs):
    _exchange_a = EXCHANGE_CLASS_MAP[Exchange[exchange_a.upper()]]()
    _exchange_b = EXCHANGE_CLASS_MAP[Exchange[exchange_b.upper()]]()
    symbol = symbol.upper()
    instType = instType.upper()
    return Spread(a=_exchange_a.ohlcv(instType, symbol), b=_exchange_b.ohlcv(instType, symbol), **kwargs)


class DataMart:
    """Unified interface to all registered Exchanges"""

    def __init__(
        self,
        exchanges: List[Exchange] = Exchange.members(),
        debug=False,
        log_file=None,
        **kwargs,
    ):
        """Unified interface to all registered Exchanges.

        Args:
            exchanges (List[Exchange], optional): Exchanges to include in the DataMart. Defaults to Exchange.members().
            debug (bool, optional): [description]. Defaults to False.
            log_file (str, optional): file to save logs to. Defaults to None.
        """
        if debug:
            self.log_level = logging.DEBUG
        if log_file is not None:
            if os.path.exists(log_file):
                logger.info(f"Removing old log file: {log_file}")
                os.remove(log_file)
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            handler = logging.FileHandler(log_file)
            handler.setFormatter(LOGGING_FORMATTER)
            logging.getLogger().addHandler(handler)

        for exchange in exchanges:
            assert exchange in Exchange.members(), f"{exchange} is not registered as an Exchange"

        self.exchange_instance_map: Dict[Exchange, ExchangeBase] = {
            exchange: EXCHANGE_CLASS_MAP[exchange](
                debug=debug,
                **kwargs,
            )
            for exchange in exchanges
        }

    @property
    def log_level(self):
        return logging.getLogger("unified_dm").level

    @log_level.setter
    def log_level(self, level):
        logging.getLogger("unified_dm").setLevel(level)

    # Exchange accessors for convenience (I am defining them so that they are picked up by Intellisense. Ideally should not be harcoding
    # exchange names like this, but the number of Exchanges implmented is not expected to change for a long time.)
    @property
    def binance(self) -> Binance:
        return self.exchange_instance_map[Exchange.BINANCE]

    @property
    def bitmex(self) -> BitMEX:
        return self.exchange_instance_map[Exchange.BITMEX]

    @property
    def bybit(self) -> Bybit:
        return self.exchange_instance_map[Exchange.BYBIT]

    @property
    def cme(self) -> CME:
        return self.exchange_instance_map[Exchange.CME]

    @property
    def coinflex(self) -> CoinFLEX:
        return self.exchange_instance_map[Exchange.COINFLEX]

    @property
    def ftx(self) -> FTX:
        return self.exchange_instance_map[Exchange.FTX]

    @property
    def gateio(self) -> GateIO:
        return self.exchange_instance_map[Exchange.GATEIO]

    @property
    def kucoin(self) -> Kucoin:
        return self.exchange_instance_map[Exchange.KUCOIN]

    @property
    def okex(self) -> OKEx:
        return self.exchange_instance_map[Exchange.OKEX]

    @property
    def exchanges(self):
        return [exchange_instance for exchange_enum, exchange_instance in self.exchange_instance_map.items()]

    def get_spreads(
        self,
        exchanges: List[Exchange],
        instType: Union[InstrumentType, List[InstrumentType]],
        symbol: Union[Symbol, List[Symbol]],
        interval: Interval,
        starttime: datetime = None,
        endtime: datetime = None,
        z_score_period: int = 30,
        use_cache_all_spreads=True,
        use_cache_combo_spreads=True,
        use_cache_ohlcv_data=True,
        refresh_cache_all_spreads=False,
        refresh_cache_combo_spreads=False,
        refresh_cache_ohlcv_data=False,
        **kwargs,
    ):
        if not isinstance(instType, list):
            instType = [instType]
        if not isinstance(symbol, list):
            symbol = [symbol]

        assert len(exchanges) > 1, "Need at least two exchanges to create spreads"

        def get_instrument_df(exchange):
            """Return all instruments for an exchange filtered by instType and Symbol"""
            exchange_obj = self.exchange_instance_map[exchange]
            instruments = exchange_obj.active_instruments
            instruments = instruments[
                np.isin(instruments["symbol"], symbol) & np.isin(instruments["instType"], instType)
            ]
            if not instruments.empty:
                instruments.loc[:, "exchange"] = exchange
            return instruments

        def create_spread(r):
            exchange_a = self.exchange_instance_map[r.exchange_a]
            exchange_b = self.exchange_instance_map[r.exchange_b]
            try:
                ohlcv_a = exchange_a.ohlcv(
                    r.instType_a,
                    r.symbol,
                    interval,
                    starttime=starttime,
                    endtime=endtime,
                    use_cache=use_cache_ohlcv_data,
                    refresh_cache=refresh_cache_ohlcv_data,
                )
                ohlcv_b = exchange_b.ohlcv(
                    r.instType_b,
                    r.symbol,
                    interval,
                    starttime=starttime,
                    endtime=endtime,
                    use_cache=use_cache_ohlcv_data,
                    refresh_cache=refresh_cache_ohlcv_data,
                )
            except MissingDataError:
                return None

            return Spread(a=ohlcv_a, b=ohlcv_b, z_score_period=z_score_period)

        @cached(
            "cache/combo_spreads",
            additional_args=[sorted(instType), sorted(symbol), interval, starttime, endtime, z_score_period],
            active=use_cache_combo_spreads,
            refresh=refresh_cache_combo_spreads,
        )
        def get_combo_spreads(exchange_a, exchange_b):
            """Return all spreads from a pair of exchanges"""
            instruments_a = get_instrument_df(exchange_a)
            instruments_b = get_instrument_df(exchange_b)
            instrument_product = instruments_a.merge(instruments_b, on="symbol", suffixes=("_a", "_b"))
            if not instrument_product.empty:
                combo_spreads = list(instrument_product.apply(create_spread, axis=1).dropna())
            else:
                combo_spreads = []
            return combo_spreads

        @cached(
            "cache/all_spreads",
            additional_args=[
                sorted(exchanges),
                sorted(instType),
                sorted(symbol),
                interval,
                starttime,
                endtime,
                z_score_period,
            ],
            active=use_cache_all_spreads,
            refresh=refresh_cache_all_spreads,
            log_level="WARNING",
        )
        def get_all_spreads():
            """Main driver function to return all spreads"""
            spreads = []
            exchange_combos = list(combinations(exchanges, 2))
            logger.info("Getting spreads")
            logger.info("Exchange combos: %s" % len(exchange_combos))
            for i, (exchange_a, exchange_b) in enumerate(exchange_combos):
                logger.info("On combo #%s" % i)
                combo_spreads = get_combo_spreads(exchange_a, exchange_b)
                spreads.extend(combo_spreads)

            logger.info("Done getting spreads")
            return spreads

        return get_all_spreads()

    def spread_details(self, spreads: List[Spread]):
        return pd.DataFrame(
            {
                "exchange_a": map(lambda e: e.ohlcv_a.exchange_name, spreads),
                "exchange_b": map(lambda e: e.ohlcv_b.exchange_name, spreads),
                "symbol": map(lambda e: e.ohlcv_b.symbol.name, spreads),
                "instType_a": map(lambda e: e.ohlcv_a.instType.name, spreads),
                "instType_b": map(lambda e: e.ohlcv_b.instType.name, spreads),
                "volatility": map(lambda e: e.volatility, spreads),
                "missing_rows": map(lambda e: len(e.missing_rows), spreads),
                "total_rows": map(lambda e: len(e), spreads),
                "earliest_time": map(lambda e: e.earliest_time, spreads),
                "latest_time": map(lambda e: e.latest_time, spreads),
                "gaps": map(lambda e: e.gaps, spreads),
                "alias": map(
                    lambda e: f"{e.ohlcv_a.exchange_name}_{e.ohlcv_a.instType.name}_{e.ohlcv_b.exchange_name}_{e.ohlcv_b.instType.name}_{e.ohlcv_b.symbol.name}",
                    spreads,
                ),
            }
        )
