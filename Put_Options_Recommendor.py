"""
Put option recommendor
"""

#%%
# Importing packages

import pandas as pd
import yfinance as yf
from datetime import datetime
import os, sys


#%%
# Function to hide the unnecessary output when downloading stocks

class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


#%%
df= pd.read_csv("ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt", sep="|")
sym = df["Symbol"]


#%%
# Finding the stocks that have option trading available

sym_op = []

for i in sym: # Iterating through Tickers
    temp = yf.Ticker(i)
    try:
        temp.options
    except:
        print("Continuing")
        continue
    print("option exists")
    sym_op.append(i)