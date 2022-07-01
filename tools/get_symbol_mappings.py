import json
import os
import sys
from io import TextIOWrapper
from typing import Union

import pandas as pd
import requests
import cryptomart as cm
from cryptomart import InstrumentType, exchanges
from cryptomart.enums import Exchange

MAPPING_COLUMNS = ["cryptomart_symbol", "exchange_symbol"]


def format_df(df: pd.DataFrame) -> pd.DataFrame:
    return df[MAPPING_COLUMNS].sort_values("cryptomart_symbol").reset_index(drop=True)


def format_mappings_as_code(df: pd.DataFrame, file: Union[str, TextIOWrapper] = None, inst_type: str = "spot") -> str:
    lines = []
    for idx, row in df.iterrows():
        # Append _ to the start of symbols that start with a number
        if row.cryptomart_symbol.startswith(tuple(str(x) for x in range(1, 9))):
            cryptomart_symbol = f"_{row.cryptomart_symbol}"
        else:
            cryptomart_symbol = row.cryptomart_symbol
        lines.append(f'    Symbol.{cryptomart_symbol}: "{row.exchange_symbol}",\n')

    def write_to_file(f):
        f.write(f"InstrumentType.{inst_type.upper()}: {{\n")
        f.writelines(lines)
        f.write("},\n")

    if file is not None:
        if isinstance(file, TextIOWrapper):
            write_to_file(file)
        else:
            with open(file, "w") as f:
                write_to_file(f)

    return "\n".join(lines)


def format_symbols_as_code(symbols: set, file: str = None) -> str:
    lines = []
    for symbol in sorted(symbols):
        if symbol.startswith(tuple(str(x) for x in range(1, 9))):
            symbol = f"_{symbol}"
        lines.append(f'    {symbol} = "{symbol}"\n')

    if file is not None:
        with open(file, "w") as f:
            f.write("class Symbol(NameEnum):\n")
            f.writelines(lines)

    return "\n".join(lines)


def get_all_symbols() -> set:
    client = cm.Client()
    
    all_symbols = set()
    for exchange in Exchange:
        perp_symbols = set(getattr(client, exchange).instrument_info("perpetual", cm.enums.Instrument.cryptomart_symbol, cache_kwargs={"refresh": True}))
        spot_symbols = set(getattr(client, exchange).instrument_info("spot", cm.enums.Instrument.cryptomart_symbol, cache_kwargs={"refresh": True}))
        all_symbols = all_symbols | perp_symbols | spot_symbols
    return all_symbols


def create_instrument_file(exchange):
    inst = exchange()
    path = os.path.join(os.getcwd(), f"cryptomart/exchanges/instrument_names/{exchange.name}.py")

    with open(path, "w") as f:
        f.write("from ...enums import InstrumentType, Symbol\n")
        f.write("instrument_names = {\n")
        for inst_type in ["perpetual", "spot"]:
            mappings = inst.get_mappings(inst_type)
            format_mappings_as_code(
                mappings,
                file=f,
            )
        f.write("}")