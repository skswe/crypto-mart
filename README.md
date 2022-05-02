# CRYPTOMART
This is a module unify the APIs of various crypto exchanges.

# Using the API
Create a `Client` object which contains the main interface for this module

```
import cryptomart as cm

client = cm.Client()
```

The client object contains a property for the following exchanges:
 - binance
 - bitmex
 - bybit
 - coinflex
 - ftx
 - gateio
 - kucoin
 - okex

# Features
## OHLCV Historical Data

```
import cryptomart as cm

client = cm.Client()

symbol = "BTC"
instType = "perpetual"
interval = cm.Interval.interval_1d
starttime = "2021-07-15"
endtime = "2022-4-30"

client.binance.ohlcv(symbol, instType, interval, starttime, endtime)
```

Out: 
```
     open_time      open      high       low     close      volume   returns
0   2021-07-15  32803.00  33170.00  31140.00  31866.43  539111.667       NaN
1   2021-07-16  31865.53  32245.00  31018.59  31382.95  516577.743 -1.517208
2   2021-07-17  31382.96  31945.00  31150.02  31496.65  422650.418  0.362299
3   2021-07-18  31496.65  32435.93  31075.10  31767.00  412189.401  0.858345
4   2021-07-19  31765.23  31890.00  30358.77  30823.62  486305.627 -2.969686
..         ...       ...       ...       ...       ...         ...       ...
284 2022-04-25  39433.40  40650.00  38111.00  40411.00  448877.893  2.479117
285 2022-04-26  40411.00  40800.00  37671.80  38093.70  453132.198 -5.734330
286 2022-04-27  38093.70  39470.00  37844.50  39209.00  385645.365  2.927781
287 2022-04-28  39209.00  40376.60  38861.80  39732.50  413543.408  1.335153
288 2022-04-29  39732.50  39924.80  38160.00  38572.20  308116.375 -2.920279

[289 rows x 7 columns]
```

OHLCV Historical data is automatically cached to the disk at `/tmp/cache`. This can be disabled by passing the `disable_cache=True` parameter to the `ohlcv` call.

## Order Book Snapshot

```
import cryptomart as cm

client = cm.Client()

symbol = "BTC"
instType = "perpetual"
depth = 20

client.binance.order_book(symbol, instType, depth)
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