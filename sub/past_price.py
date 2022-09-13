import ccxt
from datetime import datetime

binance = ccxt.binance()
ohlcvs = binance.fetch_ohlcv('ETH/USDT')

for ohlc in ohlcvs:
    print(datetime.fromtimestamp(ohlc[0]/1000).strftime('%Y-%m-%d %H:%M:%S'),end=" ")
    print("시가 : ",ohlc[1])