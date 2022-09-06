import requests
from datetime import datetime
import time
import pandas as pd
from tqdm import tqdm

result = requests.get('https://api.binance.com/api/v3/ticker/price')
js = result.json()
symbols = [x['symbol'] for x in js]
symbols_usdt = [x for x in symbols if 'USDT' in x]
for tmp in symbols_usdt:
    print(tmp)
COLUMNS = ['Open_time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close_time', 'quote_av', 'trades', 
                   'tb_base_av', 'tb_quote_av', 'ignore']
URL = 'https://api.binance.com/api/v3/klines'
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


sym = input("put in symbol : ")
#sym = sym.upper()
#sym = sym + "USDT"
start_date = input("put in start date : ")
end_date = input("put in end date : ")  #set : 2022-08-01
interv = input("put in interval : ")
get_data(start_date, end_date, sym, interv)