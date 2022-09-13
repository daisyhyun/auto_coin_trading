#프로그램 구현 전략
#래리 윌리엄스의 변동성 돌파전략으로 구매할 코인을 정함
#거래시 보조지표 rsi를 사용하여 매수/매도진행
#각 초마다 계속해서 실시간으로 데이터를 받아오며 진행한다
#백트레킹결과는 따로 존재
#포트폴리오는 노이즈 전략 또는 웹크롤링을 기반으로 한 데이터분석 또는 머신러닝가격예측을 통한 방법 중 구성
#매도는 매일 08시 0분에 진행
#각 데이터 업데이트는 09시 0분 실행

from statistics import quantiles
import time
import datetime
import ccxt
import pandas as pd
from binance.client import Client
import requests

Larry = 0.5   #변동성 돌파 전략을 위한 변수
portfolionum = 3  #포트폴리오에 들어갈 코인의 수


with open("api.txt") as f:
    lines = f.readlines()
    api_key = lines[0].strip()
    api_secret = lines[1].strip()
    binance = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret
    })


client = Client(api_key=api_key,api_secret=api_secret)


def make_sell_times(now):
    sell_time = datetime.datetime(year=now.year,
                                  month=now.month,
                                  day=now.day,
                                  hour=8,
                                  minute=0,
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

def budget():
    try:
        balance = binance.fetch_balance()
        freeusdt = float(balance['USDT']['free'])
        budget_per_coin = freeusdt / portfolionum #포트폴리오 수만큼 나눠줌
        return budget_per_coin
    except:
        return 0

def get_tickers():
    tickers = client.get_all_tickers()
    df = pd.DataFrame(data=tickers)
    df.set_index('symbol', inplace=True) # symbol , price
    return df

def target_price(ticker):
    try:
        resp = binance.fetch_ohlcv(ticker, '1d', limit=30)
        df = pd(resp, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        yesterday = df.iloc[-1]
        today_open = yesterday['close']
        yesterday_high = yesterday['high']
        yesterday_low = yesterday['low']
        target = today_open + (yesterday_high - yesterday_low) * Larry
        return target
    except:
        return None

def tickers_targets(tickers):
    targets = {}
    for ticker in tickers:
        targets[ticker] = target_price(ticker)
    return targets



def sellorder(portfolio):
    try:
        for ticker in portfolio:
            balance = binance.fetch_balance()
            freeunit = float(balance[ticker]['free'])  #현재 매도 가능한 수량
            if(freeunit > 0):
                try:
                    order = binance.create_market_sell_order(ticker)
                    time.sleep(5)
                except:
                    pass
                df = order
                df.to_csv('sellorder.csv',index=True)
    except:
        pass
    

def make_portfolio(): #해당되는 전략
    df = get_tickers()
    print(df)

now = datetime.datetime.now() #시작 시간
sell_time1, sell_time2 = make_sell_times(now)                  
setup_time1, setup_time2 = make_setup_times(now)   #매도 시간과 데이터 셋업타임 설정


result = requests.get('https://api.binance.com/api/v3/ticker/price')
js = result.json()
symbols = [x['symbol'] for x in js]
symbols_usdt = [x for x in symbols if 'USDT' in x] #마켓에서 usdt 티커를 불러옴

targets = tickers_targets(symbols_usdt)
can_buy = budget()

#포트폴리오 구성 함수 실행 -> make_portfolio()
portfolio = ['XRPUSDT,BTCUSDT,ETHUSDT']

while True:
    now = datetime.datetime.now()

    if sell_time1 < now < sell_time2: #8시에 가지고 있는 코인 전부 판매
        sellorder(portfolio)                                                  # 각 가상화폐에 대해 매도 시도                      # 당일에는 더 이상 매수되지 않도록
        time.sleep(10)

    # 09시에 시장이 초기화 되면 매수 전략 시행
    if setup_time1 < now < setup_time2:
        result = requests.get('https://api.binance.com/api/v3/ticker/price')
        js = result.json()
        symbols = [x['symbol'] for x in js]
        symbols_usdt = [x for x in symbols if 'USDT' in x]
        targets = tickers_targets(symbols_usdt)    # 목표가 갱신
