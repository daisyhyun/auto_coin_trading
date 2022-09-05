import ccxt 
import pprint

# 파일로부터 apiKey, Secret 읽기 
with open("api.txt") as f:
    lines = f.readlines()
    api_key = lines[0].strip() 
    secret = lines[1].strip() 

# binance 객체 생성
binance = ccxt.binance(config={
    'apiKey': api_key,
    'secret': secret
})

order = binance.create_limit_buy_order(
    symbol="BTC/USDT", 
    amount=0.01, 
    price=20000
)

pprint.pprint(order)