# %%
import pybithumb
import numpy as np
import pandas as pd
import seaborn
import pybithumb
import matplotlib.pyplot as plt

df = pybithumb.get_ohlcv("BTC")
df.to_csv('btc1.csv')
df = df['2017']

k = 0.5

df['range'] = (df['high'] - df['low']) * k

df['target'] = df['open'] + df['range'].shift(1)

df['larry_profit_rate'] = np.where(df['high'] > df['target'], 
                   df['close'] / df['target'],
                   1)
ror = df['larry_profit_rate'].cumprod()[-1]
print(ror)
df.to_csv('btc.csv')

plt.figure(figsize=(16, 9))
seaborn.lineplot(y=df['larry_profit_rate'], x=df.index)
plt.xlabel('day')
plt.ylabel('profit')

# %%
