import time 
import datetime
import pprint
import ccxt
from binance.client import Client
import requests
import pandas as pd
from tqdm import tqdm
import talib as ta
import pybithumb
with open("api.txt") as f:
    lines = f.readlines()
    api_key = lines[0].strip()
    api_secret = lines[1].strip()
    binance = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret
    })
    
client = Client(api_key=api_key, api_secret=api_secret)

#래리 윌리엄스의 변동성 돌파전략 
#-> 당일 시가 + 변동률*0.5
def target_price(symbol):
    df = pybithumb.get_ohlcv(symbol)
    yest = df.iloc[-2]

    open = yest['close']
    yest_high = yest['high']
    yest_low = yest['low']
    target = open +(yest_high-yest_low)*0.5 #목표가
    print(target)
    return target
# 목표가는 매일매일 계산되어야함

def buyorder(symbol,quantity,price):
    order = client.order_limit_buy(
        symbol=symbol,
        quantity=quantity,
        price=price
    )
    print(order)
    df = pd.DataFrame(order) # 매수 내역 저장
    df.to_csv('buyorder.csv',index=True)

def sellorder(symbol,quantity,price):
    order = client.order_limit_sell(
        symbol=symbol,
        quantity=quantity,
        price=price
    )
    print(order)
    df = pd.DataFrame(order) # 매도 내역 저장
    df.to_csv('sellorder.csv',index=True)
    
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

def setcandledata(symbol,time):
    from datetime import datetime, timezone
    from binance.spot import Spot as cl
    client = cl(api_key,api_secret)
    symbol = symbol #BTCUSDT로 현재 fix
    time = time #유저로부터 입력
    klines = client.klines(symbol,time,limit=200) #캔들 원하는 봉 갯수
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
    '''
    ta_stochfast,ta_stochslow = ta.STOCH(high=df['high'], low=df['low'],close=df['close'],
                fastk_period=3, slowk_period=1, slowd_period=1)
    macd,macdsig,macdhig = ta.MACD(real=df['close'],fastperiod=12,slowperiod=26,signalperiod=9)
    '''
    print(ta_rsi[-1:].values[0])
    return ta_rsi[-1:].values[0]
    #print(ta_stochfast[-1:].values[0])
    #print(ta_stochslow[-1:].values[0])
    #print(macd[-1:].values[0])
    #print(macdsig[-1:].values[0])
    #print(macdhig[-1:].values[0])


info = client.get_account()
df = pd.DataFrame(info["balances"])
df["free"] = df["free"].astype(float).round(4)
df = df[df["free"] > 0]
print(df)
portfolio = ["BTCUSDT","ETHUSDT","XRPUSDT"]
while True:
    signal = int(input("1 : see price\n2 : buy order\n3 : sell order\n4 : see past price\n5 : see future account\n6 : auto trading\n"))
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
        pprint.pprint(bids)
        balance = client.get_asset_balance(asset='USDT')
        print("your balance : ",balance)
        quantity, price = map(float,input("Input quantity and price of coin : ").split())
        buyorder(symbol,quantity,price)
    elif(signal==3):
        print("Choose what coin you want to sell") #현재 계좌에 구매하고 있는 코인들의 이름과 가격출력
        info = client.get_account()
        df = pd.DataFrame(info["balances"])
        df["free"] = df["free"].astype(float).round(4)
        df = df[df["free"] > 0]
        print(df)
        symbol = input("Input the coin symbol : ")
        quantity = float(input("Input the quantity of coin : "))
        price = float(input("Input the price : "))
        sellorder(symbol,quantity,price)
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
    elif(signal==5): #선물 계좌 보여주기
        future_account_info()
    elif(signal==6):
        ti = input("Input time stick's time(ex : 1h,1m,4h... ) : ") 
        while True:
            for x in portfolio:
                balance = binance.fetch_balance()
                freeusdt = float(balance['USDT']['free'])
                canuseusdt = freeusdt/10
                now_rsi = setcandledata(x,ti) #rsi가 20~30에서 매수, 70~80에선 매도를 하도록 구현할것
                if(now_rsi<30 and canuseusdt>=2):
                    orderbook = client.get_order_book(symbol = x)
                    asks = float(orderbook['asks'][0][0])
                    coinquan = float(orderbook['asks'][0][1])
                    buymoney = asks * coinquan
                    print(buymoney)
                    if(buymoney<freeusdt):
                        buyorder(x,coinquan,asks)
                    else:
                        coinquan = (freeusdt/asks)/2
                        buyorder(x,coinquan,asks)
                elif(now_rsi>70):
                    unit = balance[x[:-4]]['free']
                    if(unit>=0.001):
                        ret = binance.create_market_sell_order(x, unit)
                        df = pd.DataFrame(ret) # 매도 내역 저장
                        df.to_csv('sellorder.csv',index=True)
            time.sleep(60)
    elif(signal==7):
        break
                
        
        
        
                


