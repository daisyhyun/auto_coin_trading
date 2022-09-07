import time 
import datetime
import pprint
import ccxt
from binance.client import Client
import requests
import pandas as pd
from tqdm import tqdm
import talib as ta

with open("api.txt") as f:
    lines = f.readlines()
    api_key = lines[0].strip()
    api_secret = lines[1].strip()
    binance = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret
    })
    
client = Client(api_key=api_key, api_secret=api_secret)

def buyorder(symbol,quantity,price):
    order = client.order_limit_buy(
        symbol=symbol,
        quantity=quantity,
        price=price
    )
    print(order)

def sellorder(symbol,quantity,price):
    order = client.order_limit_sell(
        symbol=symbol,
        quantity=quantity,
        price=price
    )
    print(order)
def cancelorder(symbol,orderId):
    result = client.cancel_order(
        symbol=symbol,
        orderId=orderId)
    print(result)

def get_data(start_date, end_date, symbol, interv):
    data = []
    start = int(time.mktime(datetime.strptime(start_date + ' 00:00', '%Y-%m-%d %H:%M').timetuple())) * 1000
    end = int(time.mktime(datetime.strptime(end_date +' 23:59', '%Y-%m-%d %H:%M').timetuple())) * 1000
    params = {
        'symbol': symbol,
        'interval': interv,
        'limit': 1000,
        'startTime': start,
        'endTime': end
    }
    
    while start < end:
        params['startTime'] = start
        result = requests.get(URL, params = params)
        js = result.json()
        if not js:
            break
        data.extend(js) 
        start = js[-1][0] + 60000  

    df = pd.DataFrame(data)
    df.columns = COLUMNS
    df['Open_time'] = df.apply(lambda x:datetime.fromtimestamp(x['Open_time'] // 1000), axis=1)
    df = df.drop(columns = ['Close_time', 'ignore'])
    df['Symbol'] = symbol
    df.loc[:, 'Open':'tb_quote_av'] = df.loc[:, 'Open':'tb_quote_av'].astype(float) 
    df['trades'] = df['trades'].astype(int)
    print(df[['Open_time', 'Open', 'High', 'Low', 'Close', 'Volume',  'trades']])

def buyalgorithm(symbol):
    symbol = symbol
    
def future_account_info():
    infos = client.futures_position_information(symbol='BTCUSDT')   #future position
    df = pd.DataFrame(infos)
    df = df.drop(columns=['markPrice'])
    df = df.drop(columns=['isAutoAddMargin'])
    df = df.drop(columns=['maxNotionalValue'])
    df = df.drop(columns=['notional'])
    df = df.drop(columns=['isolatedMargin'])
    df = df.drop(columns=['isolatedWallet'])
    df = df.drop(columns=['updateTime'])
    print(df)

def setcandledata(symbol):
    from datetime import datetime, timezone
    from binance.spot import Spot as cl
    client = cl(api_key,api_secret)
    symbol = symbol #BTCUSDT로 현재 fix
    klines = client.klines('BTCUSDT','4h',limit=200) #캔들 원하는 봉 갯수
    df = pd.DataFrame(data={
        'open_time' : [datetime.fromtimestamp(x[0]/1000, timezone.utc) for x in klines],
        'open' : [float(x[1]) for x in klines],
        'high' : [float(x[2]) for x in klines],
        'low' : [float(x[3]) for x in klines],
        'close' : [float(x[4]) for x in klines],
        'volume' : [float(x[5]) for x in klines],
        'close_time' : [datetime.fromtimestamp(x[6]/1000,timezone.utc) for x in klines],
    })
    ta_rsi = ta.RSI(df['close'],timeperiod=14)
    print(ta_rsi[-1:].values[0])


info = client.get_account()
df = pd.DataFrame(info["balances"])
df["free"] = df["free"].astype(float).round(4)
df = df[df["free"] > 0]
print(df)

portfolio = ["BTCUSDT","ETHUSDT","XRPUSDT"]
while True:
    signal = int(input("1 : see price\n2 : buy order\n3 : sell order\n4 : see past price\n5 : see future account\n6 : see coin's rsi\n"))
    if(signal==1):
        while True:
            coin = client.get_symbol_ticker(symbol=portfolio[2])
            now = datetime.datetime.now()
            price = coin['price']
            print(now, price)
            time.sleep(1)
    elif(signal==2):
        print("Choose what coin you want to buy")
        for k in portfolio:
            print(k,end=" ")
        print()
        symbol = input("")
        orderbook = client.get_order_book(symbol=symbol)
        asks = orderbook['asks']
        bids = orderbook['bids']
        pprint.pprint(asks)
        pprint.pprint(asks)
        pprint.pprint(bids)
        
        balance = client.get_asset_balance(asset='USDT')
        print("your balance : ",balance)
        quantity, price = map(float,input("Input quantity and price of coin : ").split())
        buyorder(symbol,quantity,price)
    elif(signal==3):
        print("Choose what coin you want to sell") #현재 계좌에 구매하고 있는 코인들의 이름과 가격출력
    elif(signal==4):
        from datetime import datetime
        result = requests.get('https://api.binance.com/api/v3/ticker/price')
        js = result.json()
        symbols = [x['symbol'] for x in js]
        symbols_usdt = [x for x in symbols if 'USDT' in x]
        for tmp in symbols_usdt:
            print(tmp)
        COLUMNS = ['Open_time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close_time', 'quote_av', 'trades', 
                        'tb_base_av', 'tb_quote_av', 'ignore']
        URL = 'https://api.binance.com/api/v3/klines'
        sym = input("\nput in symbol : ")
        start_date = input("put in start date : ")
        end_date = input("put in end date : ")  #set : 2022-08-01
        interv = input("put in interval : ")
        get_data(start_date, end_date, sym, interv)
    elif(signal==5):
        future_account_info()
    elif(signal==6):
        setcandledata('BTCUSDT') #rsi가 20~30에서 매수, 70~80에선 매도를 하도록 구현할것
        
        
                

