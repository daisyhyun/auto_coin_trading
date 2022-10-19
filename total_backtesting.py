# %%

import pybithumb
import numpy as np
import pandas as pd
import seaborn
import pybithumb
import matplotlib.pyplot as plt

macd_short, macd_long, macd_signal=12,26,9 

li = ['2017','2018','2020','2021']
for tmp in li:
    df = pybithumb.get_ohlcv("BTC")
    df = df[tmp]
    df['range'] = (df['high'] - df['low']) * 0.5
    #df['rsi'] = ta.RSI(df['close'],timeperiod=14)
    df['target'] = df['open'] + df['range'].shift(1)
    df['larry_profit_rate'] = np.where(df['high'] > df['target'], 
                    df['close'] / df['target'],
                    1)
    df['change'] = df['close'] - df['close'].shift(1)
    df.loc[df['change'] >= 0, 'pchange'] = df['change']
    df.loc[df['change'] < 0, 'mchange'] = -df['change']
    df = df.fillna(0)
    df['AU'] = df['pchange'].rolling(14).mean()
    df['DU'] = df['mchange'].rolling(14).mean()
    df['RSI'] = df['AU'] / (df['AU'] + df['DU']) * 100
    df['DPR'] = df['close'].pct_change() + 1
    df.loc[df['RSI'] < 20, 'flag'] = True
    df.loc[df['RSI'] > 80, 'flag'] = False
    df["MACD_short"]=df["close"].ewm(span=macd_short).mean()
    df["MACD_long"]=df["close"].ewm(span=macd_long).mean()
    df["MACD"]=df.apply(lambda x: (x["MACD_short"]-x["MACD_long"]), axis=1)
    df["MACD_signal"]=df["MACD"].ewm(span=macd_signal).mean()  
    df["MACD_sign"]=df.apply(lambda x: ("매수" if x["MACD"]>x["MACD_signal"] else "매도"), axis=1)
    df.loc[df['flag'].shift(1) == True, 'rsibuying_'] = True
    df.loc[df['flag'].shift(1) == False, 'rsibuying_'] = False
    df['rsibuying_'].ffill(inplace=True)
    df['rsibuying_'].fillna(False, inplace=True)
    df.loc[df['MACD_sign'].shift(1) == "매수", 'macdbuying_'] = True
    df.loc[df['MACD_sign'].shift(1) == "매도", 'macdbuying_'] = False
    df['macdbuying_'].ffill(inplace=True)
    df['macdbuying_'].fillna(False, inplace=True)
    df.to_csv('btc.csv')
    df['buying_profit'] = df.loc[ df['rsibuying_'] == True & (df['macdbuying_']==True), 'DPR']
    df['buying_profit'].fillna(1, inplace=True)
    print("2021's rsi profit : ",df['buying_profit'].cumprod().iloc[-1])
    df['gen_profit'] = np.where((df['high']>df['target']) & (df['rsibuying_']==True) & (df['macdbuying_']==True), df['larry_profit_rate'],1)

    print(df['gen_profit'].cumprod()[-1])
'''
plt.figure(figsize=(16, 9))
seaborn.lineplot(y=df['gen_profit'], x=df.index)
plt.xlabel('day')
plt.ylabel('profit')
'''
# %%
