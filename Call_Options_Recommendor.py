"""
Call option recommendor 
(Initialized, Logic in progress)
"""

#%%
# Importing packages

import pandas as pd
import yfinance as yf
from datetime import datetime
import os, sys
import pickle


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
# Function to calculate percentage change from A to B

def perchange(A,B): 
    return (((B-A)/A)*100)   


#%%

class CallInvest:
    
    # Contructor
    def __init__(self):
        df= pd.read_csv("ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt", sep="|")
        self.all_sym_lst =  df["Symbol"] # All tickers on the Nasdaq exchange
        self.opt_lst = [] # Tickers with options trading
        self.final_suggestions = [] # Final list of suggested stocks
        self.opt = {"stocks":[], "last_updated": datetime.now()} # Tickers with options trading
        
    # Function to find optionable stocks
    def update_opt_stocks(self):
        temp_opt = []
        for i in self.all_sym_lst: # Iterating through all the tickers
            temp = yf.Ticker(i)
            try: # temp.options will throw an error if it doesn't exist
                temp.options
            except:
                print("Ticker ",i," doesn't support options trading")
                continue
            print("Options exist for ticker ",i)
            temp_opt.append(i)
        self.opt["stocks"] = temp_opt
        self.opt["last_updated"] = datetime.now()
    
    # Function to return the final list of suggested stocks
    def get_suggestions(self): 
        return self.final_suggestions
    
    # Function to store the object in an external file for future efficiency
    def memo(self): 
        with open('memoCall.dictionary', 'wb') as memo_dictionary_file:
            pickle.dump(self, memo_dictionary_file)
            print("object memoized!")


#%%
# Example to use the above class

with open('memoCall.dictionary', 'rb') as memo_dictionary_file: # Checking if an object has already been memoized
    obj = pickle.load(memo_dictionary_file)
    
if(obj.get_suggestions()==[]): # If the extracted object is empty, then a new object is created and memoized 
    obj = CallInvest()
    obj.check_for_updates()
    obj.get_suggestions()
    obj.memo()
else:
    obj.get_suggestions()    
