import logging

import pandas as pd
import unified_dm

logging.getLogger("unified_dm").setLevel("WARNING")
api = unified_dm.DataMart()


@unified_dm.util.cached("cache/scripts_cache", refresh=False, log_level="WARNING")
def pull_spreads(z_score_period=90, good_spreads=True, minimum_rows=180, **kwargs):
    exchange = [*unified_dm.Exchange]
    symbol = [*unified_dm.Symbol]
    instType = [*unified_dm.InstrumentType]
    interval = unified_dm.Interval.interval_1d

    spread_list = api.get_spreads(
        exchange,
        instType,
        symbol,
        interval,
        use_cache_all_spreads=True,
        use_cache_combo_spreads=True,
        refresh_cache_all_spreads=True,
        refresh_cache_combo_spreads=True,
        z_score_period=z_score_period,
    )

    spreads = pd.DataFrame({"obj": spread_list})
    details = api.spread_details(spread_list)
    spreads = pd.concat([spreads, details], axis=1)
    if good_spreads:
        spreads = spreads[
            (spreads.missing_rows == 0) & (spreads.total_rows > minimum_rows) & (spreads.gaps == 0)
        ].reset_index(drop=True)
    return spreads
