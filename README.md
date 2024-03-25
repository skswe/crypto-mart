# crypto-mart - crypto exchange data for rapid algotrading development

## Overview

The main goal of this module is to provide a unified API for accessing data
across various crypto exchanges. This module provides an interface to access the
following types of data:

- **Historical OHLCV bars (Spot / Perpetual markets)**
- **Instrument/Contract Info (Spot / perpetual markets)**
- **Historical Funding Rates (Perpetual markets only)**
- **Order Book Snapshots (Spot / Perpetual markets)**

## Installation

`git clone git@github.com:skswe/crypto-mart.git`

# A note on caching

All interfaces (except orderbook) will automatically cache the result to disk.
This design decision is enabled by default because algotrading development is an
iterative process, and running the same HTTP requests over and over while
testing code will be a waste of CPU time.

This behaviour can be disabled by passing the keyword argument
`cache_kwargs={"disabled": True}`

Example:

```
import cryptomart as cm
client = cm.Client()
df = client.ftx.ohlcv("BTC", (2022, 1, 2), (2022, 2, 5), cache_kwargs={"disabled": True})
```

The default location on disk where data is saved is `/tmp/cache`. This can be
overridden on each call by passing `cache_kwargs={"path": "/new/path/"}`. It can
also be overridden globally by setting the environment variable:
`export CM_CACHE_PATH=/new/path/` in bash or
`os.environ["CM_CACHE_PATH"] = "/new/path/"` in python

For more details on how to use / customize caching, see:
https://github.com/senderr/pyutil/blob/master/pyutil/cache.py

# Using the API

Create a `Client` object which contains the main interface for this module

```
import cryptomart as cm

client = cm.Client()
```

**Note:** on first run, the client will internally fetch instrument info for
each exchange / market. In order for the crypto-mart API to stay up to date with
new symbols added to the exchanges, pass `refresh_instruments=True` to the
client constructor.

The following exchanges are currently supported by the cryptomart API:

- binance
- bitmex
- bybit
- gateio
- kucoin
- okex

## OHLCV Historical Data

```
import cryptomart as cm

client = cm.Client()

symbol = "BTC"
inst_type = "perpetual"
starttime = "2021-07-15"
endtime = "2022-4-30"
interval = cm.Interval.interval_1d

client.binance.ohlcv(symbol, inst_type, starttime, endtime, interval)
```

Out:

```
     open_time      open      high       low     close      volume
0   2021-07-15  32803.00  33170.00  31140.00  31866.43  539111.667
1   2021-07-16  31865.53  32245.00  31018.59  31382.95  516577.743
2   2021-07-17  31382.96  31945.00  31150.02  31496.65  422650.418
3   2021-07-18  31496.65  32435.93  31075.10  31767.00  412189.401
4   2021-07-19  31765.23  31890.00  30358.77  30823.62  486305.627
..         ...       ...       ...       ...       ...         ...
284 2022-04-25  39433.40  40650.00  38111.00  40411.00  448877.893
285 2022-04-26  40411.00  40800.00  37671.80  38093.70  453132.198
286 2022-04-27  38093.70  39470.00  37844.50  39209.00  385645.365
287 2022-04-28  39209.00  40376.60  38861.80  39732.50  413543.408
288 2022-04-29  39732.50  39924.80  38160.00  38572.20  308116.375

[289 rows x 7 columns]
```

## Instrument Info

```
import cryptomart as cm

client = cm.Client()

client.kucoin.instrument_info("spot")
```

Out:

```
         symbol       name baseCurrency quoteCurrency feeCurrency market baseMinSize  ...  minFunds isMarginEnabled enableTrading cryptomart_symbol exchange_symbol exchange_list_time orderbook_multi
0       REQ-ETH    REQ-ETH          REQ           ETH         ETH   ALTS           1  ...   0.00001           False          True               REQ         REQ-ETH                NaN             1.0
1       REQ-BTC    REQ-BTC          REQ           BTC         BTC    BTC           1  ...  0.000001           False          True               REQ         REQ-BTC                NaN             1.0
2      NULS-ETH   NULS-ETH         NULS           ETH         ETH   ALTS         0.1  ...   0.00001           False          True              NULS        NULS-ETH                NaN             1.0
3      NULS-BTC   NULS-BTC         NULS           BTC         BTC    BTC         0.1  ...  0.000001           False          True              NULS        NULS-BTC                NaN             1.0
4       CVC-BTC    CVC-BTC          CVC           BTC         BTC    BTC           1  ...  0.000001           False          True               CVC         CVC-BTC                NaN             1.0
...         ...        ...          ...           ...         ...    ...         ...  ...       ...             ...           ...               ...             ...                ...             ...
1261   VSYS-BTC   VSYS-BTC         VSYS           BTC         BTC    BTC         0.1  ...  0.000001           False          True              VSYS        VSYS-BTC                NaN             1.0
1262    MKR-DAI    MKR-DAI          MKR           DAI         DAI   DeFi      0.0001  ...       0.1           False          True               MKR         MKR-DAI                NaN             1.0
1263  SOLVE-BTC  SOLVE-BTC        SOLVE           BTC         BTC    BTC          10  ...  0.000001           False          True             SOLVE       SOLVE-BTC                NaN             1.0
1264   GRIN-BTC   GRIN-BTC         GRIN           BTC         BTC    BTC        0.01  ...  0.000001           False          True              GRIN        GRIN-BTC                NaN             1.0
1265  GRIN-USDT  GRIN-USDT         GRIN          USDT        USDT   USDS        0.01  ...       0.1           False          True              GRIN       GRIN-USDT                NaN             1.0

[1264 rows x 21 columns]
```

## Order Book Snapshot

```
import cryptomart as cm

client = cm.Client()

symbol = "BTC"
inst_type = "perpetual"
depth = 20

client.binance.order_book(symbol, inst_type, depth)
```

Out:

```
      price  quantity side           timestamp
0   38595.9     7.058    b 2022-05-01 23:28:03
1   38595.8     2.829    b 2022-05-01 23:28:03
2   38595.6     0.912    b 2022-05-01 23:28:03
3   38595.1     1.060    b 2022-05-01 23:28:03
4   38595.0     0.003    b 2022-05-01 23:28:03
5   38594.9     0.200    b 2022-05-01 23:28:03
6   38594.8     0.001    b 2022-05-01 23:28:03
7   38594.5     0.440    b 2022-05-01 23:28:03
8   38594.2     1.746    b 2022-05-01 23:28:03
9   38594.1     0.526    b 2022-05-01 23:28:03
10  38593.6     1.104    b 2022-05-01 23:28:03
11  38593.5     0.926    b 2022-05-01 23:28:03
12  38593.4     0.100    b 2022-05-01 23:28:03
13  38593.1     0.001    b 2022-05-01 23:28:03
14  38592.9     0.761    b 2022-05-01 23:28:03
15  38592.7     0.002    b 2022-05-01 23:28:03
16  38592.4     0.105    b 2022-05-01 23:28:03
17  38592.2     2.000    b 2022-05-01 23:28:03
18  38592.0     0.105    b 2022-05-01 23:28:03
19  38591.8     0.285    b 2022-05-01 23:28:03
20  38596.0     5.011    a 2022-05-01 23:28:03
21  38596.1     0.004    a 2022-05-01 23:28:03
22  38596.3     0.001    a 2022-05-01 23:28:03
23  38596.4     0.029    a 2022-05-01 23:28:03
24  38596.7     0.011    a 2022-05-01 23:28:03
25  38596.8     0.076    a 2022-05-01 23:28:03
26  38596.9     0.008    a 2022-05-01 23:28:03
27  38597.0     0.002    a 2022-05-01 23:28:03
28  38597.3     0.005    a 2022-05-01 23:28:03
29  38597.5     0.025    a 2022-05-01 23:28:03
30  38597.8     0.202    a 2022-05-01 23:28:03
31  38597.9     0.620    a 2022-05-01 23:28:03
32  38598.0     1.113    a 2022-05-01 23:28:03
33  38598.2     0.413    a 2022-05-01 23:28:03
34  38598.3     0.001    a 2022-05-01 23:28:03
35  38598.4     1.368    a 2022-05-01 23:28:03
36  38598.5     0.014    a 2022-05-01 23:28:03
37  38598.6     0.001    a 2022-05-01 23:28:03
38  38598.7     0.006    a 2022-05-01 23:28:03
39  38598.8     0.008    a 2022-05-01 23:28:03
```

## Historical Funding Rate

```
import cryptomart as cm

client = cm.Client()

symbol = "BTC"
starttime = "2021-07-15"
endtime = "2022-4-30"

client.binance.funding_rate(symbol, starttime, endtime, cache_kwargs={"disabled": True})
```

Out:

```
              timestamp  funding_rate
0   2021-07-15 00:00:00     -0.000049
1   2021-07-15 08:00:00      0.000100
2   2021-07-15 16:00:00      0.000016
3   2021-07-16 00:00:00     -0.000115
4   2021-07-16 08:00:00      0.000061
..                  ...           ...
862 2022-04-28 08:00:00     -0.000055
863 2022-04-28 16:00:00      0.000100
864 2022-04-29 00:00:00      0.000100
865 2022-04-29 08:00:00      0.000100
866 2022-04-29 16:00:00      0.000026

[867 rows x 2 columns]
```
