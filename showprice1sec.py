import time 
import datetime
import pprint
from binance.client import Client
import keyboard
with open("api.txt") as f:
    lines = f.readlines()
    api_key = lines[0].strip()
    api_secret = lines[1].strip()
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
portfolio = ["BTCUSDT","ETHUSDT","XRPUSDT"]
while True:
    signal = int(input("1 : see price\n2 : buy order\n3 : sell order\n"))
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
        quantity, price = int(input("Input quantity and price of coin : ").split())
        buyorder(symbol,quantity,price)
    elif(signal==3):
        print("Choose what coin you want to sell") #현재 계좌에 구매하고 있는 코인들의 이름과 가격출력
        


