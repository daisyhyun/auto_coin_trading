#프로그램 구현 전략
#거래시 macd를 값을 구함
#해당 값들과 타켓 값이 모두 true일 때 매수/매도 실행
#각 초마다 계속해서 실시간으로 데이터를 받아오며 진행한다
#백트레킹결과는 따로 존재
#포트폴리오는 비트코인으로 픽스
#매도는 매일 08시 30분에 진행
#각 데이터 업데이트는 09시 0분 실행
#사용자가 직접 매수 매도도 가능하도록 구현


from statistics import quantiles
import time
import datetime
import ccxt
from pandas import DataFrame as pd
from binance.client import Client
import requests
import pprint


Larry = 0.5   #변동성 돌파 전략을 위한 변수

now_having = 0 #보유 BTC의 갯수


with open("api.txt") as f:
    lines = f.readlines()
    api_key = lines[0].strip()
    api_secret = lines[1].strip()
    binance = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret
    })


client = Client(api_key=api_key,api_secret=api_secret)


def budget():
    try:
        balance = binance.fetch_balance()
        freeusdt = float(balance['USDT']['free'])
        budget_per_coin = freeusdt / 2.5  
        print(freeusdt, budget_per_coin) 
        return budget_per_coin
    except:
        return 0

'''
def get_tickers():
    tickers = client.get_all_tickers()
    df = pd(data=tickers)
    df.set_index('symbol', inplace=True) # symbol , price
    return df
'''

def cur_price():
    coin = client.get_symbol_ticker(symbol=portfolio[0])
    now = datetime.datetime.now()
    price = float(coin['price'])
    print(now, price)
    return price


def target_price(ticker):
    try:
        from datetime import datetime, timezone
        from binance.spot import Spot as cl
        cli = cl(api_key,api_secret)
        symbol = ticker
        ti = '1d' #유저로부터 입력
        klines = cli.klines(symbol,ti,limit=200) #캔들 원하는 봉 갯수
        df = pd(data={
            'open_time' : [datetime.fromtimestamp(x[0]/1000, timezone.utc) for x in klines],
            'open' : [float(x[1]) for x in klines],
            'high' : [float(x[2]) for x in klines],
            'low' : [float(x[3]) for x in klines],
            'close' : [float(x[4]) for x in klines],
            'volume' : [float(x[5]) for x in klines],
            'close_time' : [datetime.fromtimestamp(x[6]/1000,timezone.utc) for x in klines],
        })
        yesterday = df.iloc[-1]
        today_open = yesterday['close']
        yesterday_high = yesterday['high']
        yesterday_low = yesterday['low']
        target = today_open + (yesterday_high - yesterday_low) * Larry
        return target
    except:
        return None


def buy_order(symbol,quantity,price):
    try:
        order = client.order_limit_buy(
            symbol=symbol,
            quantity=quantity,
            price=price
        )
        print(order)
        df = pd(order) # 매수 내역 저장
        df = df[-1]
        df.to_csv('buyorder.csv',index=True)
    except:
        pass


def buyorder(symbol,quantity):
    try:
        order = client.order_market_buy(
            symbol=symbol,
            quantity=quantity
        )
        print(order)
        df = pd(order) # 매수 내역 저장
        df = df[-1]
        df.to_csv('buyorder.csv',index=True)
    except:
        pass


def sell_order(symbol,quantity,price):
    try:
        order = client.order_limit_sell(
            symbol=symbol,
            quantity=quantity,
            price=price
        )
        print(order)
        df = pd(order) # 매도 내역 저장
        df = df[-1]
        df.to_csv('sellorder.csv',index=True)
    except:
        pass


def sellorder(ticker):
    try:
        balance = binance.fetch_balance()
        freeunit = float(balance[ticker]['free'])  #현재 매도 가능한 수량
        if(freeunit > 0):
            try:
                order = binance.create_market_sell_order(ticker)    
            except:
                pass
            df = pd(order)
            df = df[-1]
            print("매도")
            df.to_csv('sellorder.csv',index=True)
    except:
        pass

def make_sell_times(now):
    sell_time = datetime.datetime(year=now.year,
                                  month=now.month,
                                  day=now.day,
                                  hour=8,
                                  minute=30,
                                  second=0)

    sell_time_5secs = sell_time + datetime.timedelta(seconds=5) #정확한 시간을 잴 수 없기 때문에 5초의 텀
    return sell_time, sell_time_5secs


def make_setup_times(now):
    tomorrow = now + datetime.timedelta(1)
    start = datetime.datetime(year=tomorrow.year,
                                 month=tomorrow.month,
                                 day=tomorrow.day,
                                 hour=9,
                                 minute=0,
                                 second=0)
                                 
    start_5secs = start + datetime.timedelta(seconds=5)
    return start, start_5secs


def setrsiledata(symbol,ti):   #입력 봉 기준으로 200개로 rsi 구하기
    from datetime import datetime, timezone
    from binance.spot import Spot as cl
    cli = cl(api_key,api_secret)
    symbol = symbol #BTCUSDT로 현재 fix
    ti = ti #유저로부터 입력
    klines = cli.klines(symbol,ti,limit=200) #캔들 원하는 봉 갯수
    df = pd(data={
        'open_time' : [datetime.fromtimestamp(x[0]/1000, timezone.utc) for x in klines],
        'open' : [float(x[1]) for x in klines],
        'high' : [float(x[2]) for x in klines],
        'low' : [float(x[3]) for x in klines],
        'close' : [float(x[4]) for x in klines],
        'volume' : [float(x[5]) for x in klines],
        'close_time' : [datetime.fromtimestamp(x[6]/1000,timezone.utc) for x in klines],
    })
    df = df[['close']].copy()
    df1 = make_rsi(df)
    df2 = make_macd(df)
    ret_rsi = float(df1[-1:].values[0])
    ret_macd = df2[-1:].values[0]
    #print(ret_rsi, ret_macd)
    return ret_rsi, ret_macd


def make_rsi(df):
    df['change'] = df['close'] - df['close'].shift(1)
    df.loc[df['change'] >= 0, 'pchange'] = df['change']
    df.loc[df['change'] < 0, 'mchange'] = -df['change']
    df = df.fillna(0)
    df['AU'] = df['pchange'].rolling(14).mean()
    df['DU'] = df['mchange'].rolling(14).mean()
    df['RSI'] = df['AU'] / (df['AU'] + df['DU']) * 100
    df = df[['RSI']].copy()
    return df


def make_macd(df):
    macd_short, macd_long, macd_signal=12,26,9 
    df["MACD_short"]=df["close"].ewm(span=macd_short).mean()
    df["MACD_long"]=df["close"].ewm(span=macd_long).mean()
    df["MACD"]=df.apply(lambda x: (x["MACD_short"]-x["MACD_long"]), axis=1)
    df["MACD_signal"]=df["MACD"].ewm(span=macd_signal).mean()  
    df["MACD_oscillator"]=df.apply(lambda x:(x["MACD"]-x["MACD_signal"]), axis=1)
    df["MACD_sign"]=df.apply(lambda x: ("매수" if x["MACD"]>x["MACD_signal"] else "매도"), axis=1)
    df = df[['MACD_sign']].copy()
    return df


portfolio = ['BTCUSDT']
targets = target_price(portfolio[0])  
can_buy = budget()


while True:

    signal = int(input("Input your flag : "))

    if(signal==1):

        print("Choose what coin you want to buy")

        result = requests.get('https://api.binance.com/api/v3/ticker/price')
        js = result.json()
        symbols = [x['symbol'] for x in js]
        symbols_usdt = [x for x in symbols if 'USDT' in x]

        for k in symbols_usdt:
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
        buy_order(symbol,quantity,price)

    elif(signal==2):
    
        print("Choose what coin you want to sell") #현재 계좌에 구매하고 있는 코인들의 이름과 가격출력
        
        info = client.get_account()
        df = pd(info["balances"])
        df["free"] = df["free"].astype(float).round(4)
        df = df[df["free"] > 0]
        print(df)

        symbol = input("Input the coin symbol : ")
        quantity = float(input("Input the quantity of coin : "))
        price = float(input("Input the price : "))

        sellorder(symbol,quantity,price)

    elif(signal==5):

        print("start program")

        signal = int(input(" Press 1 to use RSI \nPress 2 to use  Larry R. Williams \nPress 3 to use MACD \nPress 4 to use MACD and Larry : "))

        if(signal==1):

            num_candle = input("Input indicator's candle nums : ")

            while True:
                can_budget = budget()
                prices = cur_price()

                # 매수
                now_rsi, now_macd = setrsiledata(portfolio[0],num_candle)

                if(now_rsi<20):

                    print("매수")
                    print(can_budget/prices)
                    quan = round(can_budget/prices,5)
                    buy_order(portfolio[0],quan,prices)

                #매도
                if(now_rsi>80):

                    print("매도")
                    sellorder(portfolio[0])

                time.sleep(1)

        elif(signal==2):

            now = datetime.datetime.now() 

            sell_time1, sell_time2 = make_sell_times(now)                  
            setup_time1, setup_time2 = make_setup_times(now)   

            while True:

                now = datetime.datetime.now()
                
                if sell_time1 < now < sell_time2: 
                    sellorder(portfolio[0])                                                               
                    time.sleep(5)
                
                if setup_time1 < now < setup_time2: 

                    targets = target_price(portfolio[0])   

                    can_budget = budget()   
                    sell_time1, sell_time2 = make_sell_times(now)      
                    setup_time1, setup_time2 = make_setup_times(now)  

                    time.sleep(10)

                can_budget = budget()
                prices = cur_price()

                # 매수

                if(prices<targets[portfolio[0]]):
                    print("매수")
                    print(can_budget/prices)
                    quan = round(can_budget/prices,5)
                    buy_order(portfolio[0],quan,prices)

                time.sleep(1)

        elif(signal==3):

            num_candle = input("Input indicator's candle nums : ")

            while True:

                can_budget = budget()
                prices = cur_price()

                # 매수

                now_rsi, now_macd = setrsiledata(portfolio[0],num_candle)

                if(now_macd =='매수'):

                    print("매수")
                    print(can_budget/prices)
                    quan = round(can_budget/prices,5)
                    buy_order(portfolio[0],quan,prices)

                #매도
                if(now_macd =='매도'):
                
                    sellorder(portfolio[0])

                time.sleep(1)

        elif(signal==4):

            now = datetime.datetime.now() 
            sell_time1, sell_time2 = make_sell_times(now)                  
            setup_time1, setup_time2 = make_setup_times(now)  

            num_candle = input("Input indicator's candle nums : ")

            while True:

                now = datetime.datetime.now()

                if sell_time1 < now < sell_time2: 
                    sellorder(portfolio[0])                                                               
                    time.sleep(5)
                
                if setup_time1 < now < setup_time2:  

                    
                    targets = target_price(portfolio[0])    

                    can_budget = budget()   
                    sell_time1, sell_time2 = make_sell_times(now)      
                    setup_time1, setup_time2 = make_setup_times(now)  
                    time.sleep(10)

                can_budget = budget()
                prices = cur_price()

                # 매수

                now_rsi, now_macd = setrsiledata(portfolio[0],num_candle)

                if(now_macd =='매수' and prices<targets[portfolio[0]]):
                    print("매수")
                    print(can_budget/prices)
                    quan = round(can_budget/prices,5)
                    buy_order(portfolio[0],quan,prices)

                #매도

                if(now_macd =='매도'):
                
                    sellorder(portfolio[0])

                time.sleep(1)
