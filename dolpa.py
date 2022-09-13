import time
import datetime
import ccxt
import pandas as pd
from binance.client import Client

from binance.spot import Spot as cl
with open("api.txt") as f:
    lines = f.readlines()
    api_key = lines[0].strip()
    api_secret = lines[1].strip()
    binance = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret
    })
client = Client(api_key=api_key,api_secret=api_secret)

Larry = 0.5 #변동성돌파 변수(0.2~1.4 0.1간격)

# 목표가는 매일매일 계산되어야함
symbol = "BTCUSDT"
interval ='1h'
def target_price(symbol):
    btc = binance.fetch_ohlcv(
        symbol=symbol,timeframe='1d',
        since=None,limit=10)
    df = pd.DataFrame(
        data=btc, 
        columns=['datetime', 'open', 'high', 'low', 'close', 'volume']
    )
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
    df.set_index('datetime', inplace=True)

    yesterday = df.iloc[-2]
    today = df.iloc[-1]
    target = today['open'] + (yesterday['high'] - yesterday['low']) * Larry
    print(target)
    return target

def get_tickers():
    tickers = client.get_all_tickers()
    df = pd.DataFrame(data=tickers)
    df.set_index('symbol', inplace=True) # symbol , price
    df

def interval_price(symbol,interval): # 
    from datetime import datetime, timezone
    cli = cl(api_key,api_secret)
    klines = cli.klines(symbol,interval,limit=200) #캔들 원하는 봉 갯수
    df = pd.DataFrame(data={
        'open_time' : [datetime.fromtimestamp(x[0]/1000, timezone.utc) for x in klines],
        'open' : [float(x[1]) for x in klines],
        'high' : [float(x[2]) for x in klines],
        'low' : [float(x[3]) for x in klines],
        'close' : [float(x[4]) for x in klines],
        'volume' : [float(x[5]) for x in klines],
        'close_time' : [datetime.fromtimestamp(x[6]/1000,timezone.utc) for x in klines],
    })
    
interval_price(symbol,interval)

while True:
    now = datetime.datetime.now()
    if now.hour == 9 and now.minute==0:
        target = target_price(symbol)
    btc = client.get_symbol_ticker(symbol=symbol)
    print(now,btc['price'])
 #   if(target>btc): 변동성이 돌파하면 매수주문
 #       buyorder
#   elif(target<btc): 변동성이 돌파하지못하면 매도
#        sellorder   
    time.sleep(1)
