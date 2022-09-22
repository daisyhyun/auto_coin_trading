# %%
import pybithumb
import numpy as np
import pandas as pd
import seaborn
import pybithumb
import matplotlib.pyplot as plt

df = pybithumb.get_ohlcv("BTC")
df.to_csv('btc1.csv')
df = df.loc['2021']
k = 0.8

df['range'] = (df['high'] - df['low']) * k

df['target'] = df['open'] + df['range'].shift(1)

df['larry_profit_rate'] = np.where(df['high'] > df['target'], 
                   df['close'] / df['target'],
                   1)
df.to_csv('btc.csv')

plt.figure(figsize=(16, 9))
seaborn.lineplot(y=df['larry_profit_rate'], x=df.index)
plt.xlabel('day')
plt.ylabel('profit')
print("2021's profit : ",df['larry_profit_rate'].cumprod().iloc[-1])

# %%
