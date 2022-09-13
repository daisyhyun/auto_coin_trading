import time
import datetime
import ccxt
from pandas import DataFrame

#순서 : 트레이딩 시간설정, 이동평균 산, 노이즈 계산으로 포트폴리오 선정, 매매
#계좌 불러오기
MIN_ORDERS = {}
MIN_AMOUNT = {}
with open("api.txt") as f:
    lines = f.readlines()
    api_key = lines[0].strip() 
    secret = lines[1].strip()  #파일로부터 apikey 읽기
    
    binance = ccxt.binance(config={ # binance 객체 생성
        'apiKey': api_key,
        'secret': secret
    })
    resp = binance.load_markets() #마켓 불러오기
    for k, v in resp.items():
        MIN_ORDERS[k] = v['limits']['amount']['min']
        MIN_AMOUNT[k] = v['limits']['cost']['min']
def now_balance():   #현재 잔고를 보여줌
    balance = binance.fetch_balance()
    print(balance['USDT'])
    return None

def current_coin_price(tickers): #코인의 현재가 출력
    try:
        all = binance.fetch_tickers()
        return {ticker: all[ticker]['ask'] for ticker in tickers}
    except:
        return None

def highest_coin_price(tickers):
    try:
        resp = binance.fetch_tickers()
        high_prices = {x:resp[x]['high'] for x in tickers}
        return high_prices
    except:
        return  {ticker:0 for ticker in tickers}

def buy_order(ticker,amount,price):
    try:
        order = binance.create_market_buy_order(ticker,amount,price)
        print("BUY ",order)
    except:
        pass

def sell_order_all(tickers):
    try:
        for ticker in tickers:
            unit = binance.fetch_balance(ticker)[ticker]['free']
            ret = binance.create_market_sell_order(ticker, unit)
            print("SELL ALL", ticker, unit)
    except:
        pass

def sell_order(ticker,amount,price):
    try:
        order = binance.create_limit_sell_order(ticker,amount,price)
        print("SELL",ticker,amount,price)
    except:
        pass

balance = binance.fetch_balance() #현재 usdt 잔고
print(balance['USDT'])