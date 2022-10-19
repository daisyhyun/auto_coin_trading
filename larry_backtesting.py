# %%
import pybithumb
import numpy as np
import pandas as pd
import seaborn
import pybithumb
import matplotlib.pyplot as plt


li = ['2017','2018','2020','2021']
for tmp in li:
    df = pybithumb.get_ohlcv("BTC")
    df = df.loc[tmp]
    k = 0.5

    df['range'] = (df['high'] - df['low']) * k

    df['target'] = df['open'] + df['range'].shift(1)

    df['larry_profit_rate'] = np.where(df['high'] > df['target'], 
                    df['close'] / df['target'],
                    1)
                    
    df.to_csv('larry.csv')
    plt.figure(figsize=(16, 9))
    seaborn.lineplot(y=df['larry_profit_rate'], x=df.index)
    plt.xlabel('day')
    plt.ylabel('profit')
    print("profit : ",df['larry_profit_rate'].cumprod().iloc[-1])

# %%
