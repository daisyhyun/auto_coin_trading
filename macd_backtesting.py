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
    df = df[['close']].copy( )

    macd_short, macd_long, macd_signal=12,26,9 
    #macd_short, macd_long, macd_signal=5,34,7
    #macd_short, macd_long, macd_signal=9,26,9 
    #12-26-9,5-34-7,9-26-9
    df["MACD_short"]=df["close"].ewm(span=macd_short).mean()
    df["MACD_long"]=df["close"].ewm(span=macd_long).mean()
    df["MACD"]=df.apply(lambda x: (x["MACD_short"]-x["MACD_long"]), axis=1)
    df["MACD_signal"]=df["MACD"].ewm(span=macd_signal).mean()  
    #df["MACD_oscillator"]=df.apply(lambda x:(x["MACD"]-x["MACD_signal"]), axis=1)
    df["MACD_sign"]=df.apply(lambda x: ("매수" if x["MACD"]>x["MACD_signal"] else "매도"), axis=1)
    df['DPR'] = df['close'].pct_change() + 1
    df.loc[df['MACD_sign'].shift(1) == "매수", 'buying_'] = True
    df.loc[df['MACD_sign'].shift(1) == "매도", 'buying_'] = False
    df['buying_'].ffill(inplace=True)
    df['buying_'].fillna(False, inplace=True)
    df['buying_profit'] = df.loc[ df['buying_'] == True, 'DPR']
    df['buying_profit'].fillna(1, inplace=True)


    df.to_csv("macd_back.csv")

    plt.figure(figsize=(16, 9))
    seaborn.lineplot(y=df['buying_profit'], x=df.index)
    plt.xlabel('day')
    plt.ylabel('profit')

    print("macd profit : ",df['buying_profit'].cumprod().iloc[-1])
# %%
