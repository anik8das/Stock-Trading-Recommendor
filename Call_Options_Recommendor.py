# -*- coding: utf-8 -*-
"""

Spyder Editor

This is an options trading recommendor

"""

#%%
# Defining a function to hide the unnecessary output when downloading stocks

import os, sys

class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout
    
#%%
# Importing packages

import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
from datetime import datetime
from datetime import timedelta
import numpy as np

#%%
# Defining dates and getting the tickers of all the stocks

tod = datetime.date(datetime.now())
prevtod = tod - timedelta(days = 60)
prevyear = tod - timedelta(days = 365)
yday = tod - timedelta(days = 1)
tod = tod.strftime("%Y-%m-%d")
prevtod = prevtod.strftime("%Y-%m-%d")
prevyear = prevyear.strftime("%Y-%m-%d")
yday = yday.strftime("%Y-%m-%d")
df= pd.read_csv("ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt", sep="|")


#%%
baba = yf.download("BABA", start = prevtod, end = tod)
plt.plot(baba["Close"])


#%%
# Finding the stocks that have moved the highest

sym = df["Symbol"]
symlist = []
for i in sym: # Iterating through Tickers
    temp = yf.Ticker(i)
    if(temp.options == ()): # Only continuing if options for the Stock exist
        continue
    with HiddenPrints(): # Hiding the unnecessary output while downloading 
        data = yf.download(i,start = prevtod, end = tod)
    if(len(data)>=2): # Continuing only if the data is non-empty
        chng = ((data["Adj Close"][-1] - data["Adj Close"][-2]) / data["Adj Close"][-2]) * 100 # calculating the change in the single last day
        if(chng <= -3): # If the stock dropped by more than 5%
            data1 = yf.download(i, start = prevyear, end = tod)
            meanrec = np.mean(data1.loc["Adj Close"][-10:-2]) 
            meanold = np.mean(data1.loc["Adj Close"][0:10])
            if((meanrec - meanold)/meanold > 0.25): # Comparing running mean values from the start till the end of the year
                midmean = np.mean(data1.loc["Adj Close"][177:187])
                lhm = (meanrec+meanold)/2
                if(midmean > 0.85*lhm and midmean < 1.15*lhm):
                    symlist.append(i)
        else:
            monmean = np.mean(data.loc[prevtod:yday]["Adj Close"])
            chng = (data["Adj Close"][-1] - monmean)/monmean * 100
            if(chng < -3):
                data1 = yf.download(i, start = prevyear, end = tod)
                meanrec = np.mean(data1.loc["Adj Close"][-11:-2])
                meanold = np.mean(data1.loc["Adj Close"][0:10])
                if((meanrec - meanold)/meanold > 0.25):
                    midmean = np.mean(data1.loc["Adj Close"][177:187])
                    lhm = (meanrec+meanold)/2
                    if(midmean > 0.85*lhm and midmean < 1.15*lhm):
                        symlist.append(i)
                else:
                    cv = np.std(data1.loc[prevtod:yday]["Adj Close"])/monmean
                    if(cv > 0.1 and (meanrec - meanold)/meanold > - 0.05):
                        symlist.append(i)
    
#%%
data = yf.download("AAL", start = prevtod, end = tod)
plt.plot(data["Adj Close"])
monmean = np.mean(data.loc[prevtod:yday]["Adj Close"])
chng = (data["Adj Close"][-1] - monmean)/monmean * 100
print(monmean, data["Adj Close"][-1],chng)

#%%
data = yf.Ticker("TBIO")
print(data.recommendation)