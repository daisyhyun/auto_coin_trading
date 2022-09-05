import ccxt

exchange = ccxt.binance()
orderbook = exchange.fetch_order_book('ETH/USDT')
print(orderbook['asks'])
print(orderbook['bids'])