import json
import os
import sys
from io import TextIOWrapper
from typing import Union

import pandas as pd
import requests
from cryptomart import InstrumentType, exchanges

MAPPING_COLUMNS = ["cryptomart_symbol", "exchange_symbol"]


def format_df(df: pd.DataFrame) -> pd.DataFrame:
    return df[MAPPING_COLUMNS].sort_values("cryptomart_symbol").reset_index(drop=True)


def format_mappings_as_code(df: pd.DataFrame, file: Union[str, TextIOWrapper] = None, instType: str = "spot") -> str:
    lines = []
    for idx, row in df.iterrows():
        # Append _ to the start of symbols that start with a number
        if row.cryptomart_symbol.startswith(tuple(str(x) for x in range(1, 9))):
            cryptomart_symbol = f"_{row.cryptomart_symbol}"
        else:
            cryptomart_symbol = row.cryptomart_symbol
        lines.append(f'    Symbol.{cryptomart_symbol}: "{row.exchange_symbol}",\n')

    def write_to_file(f):
        f.write(f"InstrumentType.{instType.upper()}: {{\n")
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
    all_symbols = set()
    for exchange in Binance, FTX, Bybit, OKEx, CoinFLEX, BitMEX, GateIO, Kucoin:
        perp_symbols = set(exchange().get_mappings("perpetual").cryptomart_symbol.to_list())
        spot_symbols = set(exchange().get_mappings("spot").cryptomart_symbol.to_list())
        all_symbols = all_symbols | perp_symbols | spot_symbols
    return all_symbols


def create_instrument_file(exchange):
    inst = exchange()
    path = os.path.join(os.getcwd(), f"cryptomart/exchanges/instrument_names/{exchange.name}.py")

    with open(path, "w") as f:
        f.write("from ...enums import InstrumentType, Symbol\n")
        f.write("instrument_names = {\n")
        for instType in ["perpetual", "spot"]:
            mappings = inst.get_mappings(instType)
            format_mappings_as_code(
                mappings,
                file=f,
            )
        f.write("}")


class Binance(exchanges.Binance):
    ACCEPTED_QUOTE_ASSETS = {InstrumentType.PERPETUAL: ["USDT"], InstrumentType.SPOT: ["USDT"]}

    def get_mappings(self, instType: InstrumentType) -> pd.DataFrame:
        base_url = self._base_url if instType == InstrumentType.SPOT else self._futures_base_url
        suburl = "api/v3/exchangeInfo" if instType == InstrumentType.SPOT else "fapi/v1/exchangeInfo"
        url = os.path.join(base_url, suburl)
        quote_assets = self.ACCEPTED_QUOTE_ASSETS[instType]

        res = requests.get(url)
        data = pd.DataFrame(res.json()["symbols"])

        data = data[data.status == "TRADING"]
        data = data[data.quoteAsset.isin(quote_assets)]

        data["cryptomart_symbol"] = data["baseAsset"]
        data["exchange_symbol"] = data["symbol"]

        return format_df(data)


class BitMEX(exchanges.BitMEX):
    ACCEPTED_QUOTE_ASSETS = {InstrumentType.PERPETUAL: ["USDT"], InstrumentType.SPOT: ["USDT"]}

    def get_mappings(self, instType: InstrumentType) -> pd.DataFrame:
        base_url = self._base_url
        url = os.path.join(base_url, "instrument")
        quote_assets = self.ACCEPTED_QUOTE_ASSETS[instType]

        exchange_instType = {
            InstrumentType.PERPETUAL: "FFWCSX",
            InstrumentType.SPOT: "IFXXXP",
        }[instType]

        filter = {
            "typ": exchange_instType,
            "state": "Open",
            "quoteCurrency": quote_assets,
        }
        params = {"filter": json.dumps(filter)}

        res = requests.get(url, params=params)
        data = pd.DataFrame(res.json())

        data["cryptomart_symbol"] = data["underlying"]
        data["exchange_symbol"] = data["symbol"]

        return format_df(data)


class Bybit(exchanges.Bybit):
    ACCEPTED_QUOTE_ASSETS = {InstrumentType.PERPETUAL: ["USDT"], InstrumentType.SPOT: ["USDT"]}

    def get_mappings(self, instType: InstrumentType) -> pd.DataFrame:
        # Bybit has the same symbols for PERPs and SPOT
        base_url = self._base_url
        url = os.path.join(base_url, "v2/public/symbols")
        quote_assets = self.ACCEPTED_QUOTE_ASSETS[instType]

        res = requests.get(url)
        data = pd.DataFrame(res.json()["result"])

        data = data[data.status == "Trading"]

        # filter out symbols that end in a number
        data = data[data.name.apply(lambda e: e[-1] not in [str(x) for x in range(0, 9)])]

        data = data[data.quote_currency.isin(quote_assets)]

        data["cryptomart_symbol"] = data["base_currency"]
        data["exchange_symbol"] = data["name"]

        return format_df(data)


class CoinFLEX(exchanges.CoinFLEX):
    ACCEPTED_QUOTE_ASSETS = {InstrumentType.PERPETUAL: ["USD"], InstrumentType.SPOT: ["USD"]}

    def get_mappings(self, instType: InstrumentType) -> pd.DataFrame:
        # Bybit has the same symbols for PERPs and SPOT
        base_url = self._base_url
        url = os.path.join(base_url, "v3/markets")
        quote_assets = self.ACCEPTED_QUOTE_ASSETS[instType]
        type_filter = "SPOT" if instType == InstrumentType.SPOT else "FUTURE"

        res = requests.get(url)

        data = pd.DataFrame(res.json()["data"])

        data = data[data.type == type_filter]

        data = data[data.counter.isin(quote_assets)]

        data["cryptomart_symbol"] = data["base"]
        data["exchange_symbol"] = data["marketCode"]

        return format_df(data)


class FTX(exchanges.FTX):
    ACCEPTED_QUOTE_ASSETS = {InstrumentType.PERPETUAL: ["USDT"], InstrumentType.SPOT: ["USD"]}

    def get_mappings(self, instType: InstrumentType) -> pd.DataFrame:
        base_url = self._base_url
        url = os.path.join(base_url, "markets")
        quote_assets = self.ACCEPTED_QUOTE_ASSETS[instType]
        type_filter = "spot" if instType == InstrumentType.SPOT else "future"

        res = requests.get(url)
        data = pd.DataFrame(res.json()["result"])

        data = data[data.enabled]
        data = data[data.type == type_filter]
        data = data[~data.isEtfMarket]
        data = data[~data.restricted]

        if instType == InstrumentType.PERPETUAL:
            data = data[data.name.apply(lambda e: e.endswith("PERP"))]
            data["cryptomart_symbol"] = data["underlying"]
        elif instType == InstrumentType.SPOT:
            data = data[data.quoteCurrency.isin(quote_assets)]
            data["cryptomart_symbol"] = data["baseCurrency"]

        data["exchange_symbol"] = data["name"]

        return format_df(data)


class GateIO(exchanges.GateIO):
    ACCEPTED_QUOTE_ASSETS = {InstrumentType.PERPETUAL: ["USDT"], InstrumentType.SPOT: ["USDT"]}

    def get_mappings(self, instType: InstrumentType) -> pd.DataFrame:
        base_url = self._base_url
        suburl = "spot/currency_pairs" if instType == InstrumentType.SPOT else "futures/usdt/contracts"
        url = os.path.join(base_url, suburl)
        quote_assets = self.ACCEPTED_QUOTE_ASSETS[instType]

        res = requests.get(url)
        data = pd.DataFrame(res.json())

        if instType == InstrumentType.PERPETUAL:
            data = data[data.in_delisting == False]
            data = data[data.type == "direct"]
            data["cryptomart_symbol"] = data.name.apply(lambda e: e.replace(f"_{quote_assets[0]}", ""))
            data["exchange_symbol"] = data["name"]
        elif instType == InstrumentType.SPOT:
            data = data[data.trade_status == "tradable"]
            data = data[data.quote.isin(quote_assets)]
            data["cryptomart_symbol"] = data["base"]
            data["exchange_symbol"] = data["id"]

        return format_df(data)


class Kucoin(exchanges.Kucoin):
    ACCEPTED_QUOTE_ASSETS = {InstrumentType.PERPETUAL: ["USDT"], InstrumentType.SPOT: ["USDT"]}

    def get_mappings(self, instType: InstrumentType) -> pd.DataFrame:
        base_url = self._base_url if instType == InstrumentType.SPOT else self._futures_base_url
        suburl = "api/v1/symbols" if instType == InstrumentType.SPOT else "api/v1/contracts/active"
        url = os.path.join(base_url, suburl)
        quote_assets = self.ACCEPTED_QUOTE_ASSETS[instType]

        res = requests.get(url)
        data = pd.DataFrame(res.json()["data"])

        data = data[data.quoteCurrency.isin(quote_assets)]

        if instType == InstrumentType.PERPETUAL:
            data = data[data.status == "Open"]
            data = data[data.isInverse == False]
        elif instType == InstrumentType.SPOT:
            data = data[data.enableTrading == True]

        data["cryptomart_symbol"] = data["baseCurrency"]
        data["exchange_symbol"] = data["symbol"]

        return format_df(data)


class OKEx(exchanges.OKEx):
    ACCEPTED_QUOTE_ASSETS = {InstrumentType.PERPETUAL: ["USDT"], InstrumentType.SPOT: ["USDT"]}

    def get_mappings(self, instType: InstrumentType) -> pd.DataFrame:
        # Bybit has the same symbols for PERPs and SPOT
        base_url = self._base_url
        url = os.path.join(base_url, "public/instruments")

        exchange_instType = {
            InstrumentType.PERPETUAL: "SWAP",
            InstrumentType.SPOT: "SPOT",
        }[instType]

        params = {"instType": exchange_instType}
        quote_assets = self.ACCEPTED_QUOTE_ASSETS[instType]

        res = requests.get(url, params=params)

        data = pd.DataFrame(res.json()["data"])

        data = data[data.state == "live"]
        if instType == InstrumentType.PERPETUAL:
            data = data[data.ctType == "linear"]
            data = data[data.settleCcy.isin(quote_assets)]

            data["cryptomart_symbol"] = data["ctValCcy"]
            data["exchange_symbol"] = data["instId"]
        else:
            data = data[data.quoteCcy.isin(quote_assets)]

            data["cryptomart_symbol"] = data["baseCcy"]
            data["exchange_symbol"] = data["instId"]

        return format_df(data)
