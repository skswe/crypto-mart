import unified_dm

api = unified_dm.DataMart(
    debug=True, log_file="logs/pull_all_spreads.log", use_instruments_cache=True, refresh_instruments_cache=False
)

exchange = [*unified_dm.Exchange]
symbol = [*unified_dm.Symbol]
instType = [*unified_dm.InstrumentType]
interval = unified_dm.Interval.interval_1d

spread_list = api.get_spreads(
    exchange,
    instType,
    symbol,
    interval,
    refresh_cache_all_spreads=False,
    refresh_cache_combo_spreads=False,
    z_score_period=90,
)
