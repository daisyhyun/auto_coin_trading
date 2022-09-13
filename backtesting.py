import pybithumb
import numpy as np
import talib as ta

df = pybithumb.get_ohlcv("BTC")
df = df['2018']
df['range'] = (df['high'] - df['low']) * 0.5
#df['rsi'] = ta.RSI(df['close'],timeperiod=14)
df['target'] = df['open'] + df['range'].shift(1)
df['larry_profit_rate'] = np.where(df['high'] > df['target'], 
                   df['close'] / df['target'],
                   1)
#df['buy_signal'] = np.where(df['rsi']<30,df['close'],0)
#df['sell_signal'] = np.where(df['buy_signal']==0,0,df['close']-df[''])
ror = df['larry_profit_rate'].cumprod()[-2]
print(ror)
df.to_csv('btc.csv')