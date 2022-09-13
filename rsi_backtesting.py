# %%
import pybithumb
import numpy as np
import talib as ta
import matplotlib.pyplot as plt
import seaborn; seaborn.set
import pandas as pd
df = pybithumb.get_ohlcv("BTC")
#df = df[['close']].copy()
#print(df)
df = df['2017']
df = df[['close']].copy( )
#df.flags.allows_duplicate_labels = False
df['change'] = df['close'] - df['close'].shift(1)
df.loc[df['change'] >= 0, 'pchange'] = df['change']
df.loc[df['change'] < 0, 'mchange'] = -df['change']
df = df.fillna(0)
df['AU'] = df['pchange'].rolling(14).mean()
df['DU'] = df['mchange'].rolling(14).mean()
df['RSI'] = df['AU'] / (df['AU'] + df['DU']) * 100
df['DPR'] = df['close'].pct_change() + 1
df.loc[df['RSI'] < 30, 'flag'] = True
df.loc[df['RSI'] > 70, 'flag'] = False
df.loc[df['flag'].shift(1) == True, 'buying_'] = True
df.loc[df['flag'].shift(1) == False, 'buying_'] = False

df['buying_'].ffill(inplace=True)
df['buying_'].fillna(False, inplace=True)
df['buying_profit'] = df.loc[ df['buying_'] == True, 'DPR']
df['buying_profit'].fillna(1, inplace=True)
print(df['buying_profit'].cumprod().iloc[-1])
df.to_csv('rsi_trade.csv')

df = pd.read_csv('rsi_trade.csv')
df = df[['time','buying_profit']]
profit = np.array(df)

#print(df['buying_profit'].cumprod().iloc[-2])
#profit = np.array(df['buying_profit'])

plt.hist(profit)
plt.xlabel('day')
plt.ylabel('profit_rate')
#df.to_csv('rsi_trade.csv')
# %%
