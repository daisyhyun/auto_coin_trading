from binance.client import Client
client = Client(api_key="", api_secret="")
balance = client.get_asset_balance(asset='USDT')
print(balance)

