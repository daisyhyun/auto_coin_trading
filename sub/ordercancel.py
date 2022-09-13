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

resp = binance.cancel_order(
    id=5221422745,  # order 객체 안에 있는 id값
    symbol='BTC/USDT'
)

pprint.pprint(resp)