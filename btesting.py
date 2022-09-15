# %%

import pybithumb
import numpy as np
import pandas as pd
import seaborn
import pybithumb
import matplotlib.pyplot as plt

df = pybithumb.get_ohlcv("BTC")
df = df['2022']
df['range'] = (df['high'] - df['low']) * 0.5
#df['rsi'] = ta.RSI(df['close'],timeperiod=14)
df['target'] = df['open'] + df['range'].shift(1)
df['larry_profit_rate'] = np.where(df['high'] > df['target'], 
                   df['close'] / df['target'],
                   1)
print(df['larry_profit_rate'].cumprod()[-1])
'''
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


df['gen_profit'] = np.where((df['high']>df['target']) & (df['buying_']==True), df['larry_profit_rate'],1)
'''

print(df['buying_profit'].cumprod()[-1])
plt.figure(figsize=(16, 9))
seaborn.lineplot(y=df['buying_profit'], x=df.index)
plt.xlabel('day')
plt.ylabel('profit')
'''
print(df['gen_profit'].cumprod()[-1])
plt.figure(figsize=(16, 9))
seaborn.lineplot(y=df['gen_profit'], x=df.index)
plt.xlabel('day')
plt.ylabel('profit')
'''
# %%
