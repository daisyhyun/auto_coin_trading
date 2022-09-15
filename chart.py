# %%

import seaborn
import pybithumb
import matplotlib.pyplot as plt


df = pybithumb.get_ohlcv("BTC")
plt.figure(figsize=(16, 9))
seaborn.lineplot(y=df['close'], x=df.index)
plt.xlabel('time')
plt.ylabel('price')
# %%
