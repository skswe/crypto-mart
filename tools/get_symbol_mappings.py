import json
import os
import sys

import pandas as pd
import requests
from cryptomart import InstrumentType, exchanges

MAPPING_COLUMNS = ["cryptomart_symbol", "exchange_symbol"]


def format_df(df: pd.DataFrame) -> pd.DataFrame:
    return df[MAPPING_COLUMNS].sort_values("cryptomart_symbol").reset_index(drop=True)


def format_as_code(df: pd.DataFrame, file: str = None) -> str:
    lines = []
    for idx, row in df.iterrows():
        lines.append(f'{row.cryptomart_symbol} = "{row.exchange_symbol}"')

    if file is not None:
        with open(file, "w") as f:
            f.writelines(lines)

    return "\n".join(lines)


class Binance(exchanges.Binance):
    ACCEPTED_QUOTE_ASSETS = {InstrumentType.PERPETUAL: ["USDT"], InstrumentType.SPOT: ["USDT"]}

    def get_mappings(self, instType):
        base_url = self._base_url if instType == InstrumentType.SPOT else self._futures_base_url
        url = os.path.join(base_url, "exchangeInfo")
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

    def get_mappings(self, instType):
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

    def get_mappings(self, instType):
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

    def get_mappings(self, instType):
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

    def get_mappings(self, instType):
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


class OKEx(exchanges.OKEx):
    ACCEPTED_QUOTE_ASSETS = {InstrumentType.PERPETUAL: ["USDT"], InstrumentType.SPOT: ["USDT"]}

    def get_mappings(self, instType):
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
