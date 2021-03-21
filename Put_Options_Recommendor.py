"""
Put option recommendor

Stocks are checked for:
    1. An underperform analyst rating at most
    2. Either an increase of at least 40% or a decrease of at least 20%
    3. A decrease in speculated Price to Earnings ratio by at least 10%
    4. Suggested stocks are updated every 30 days
    5. The parameters can be modified through the constructor
    6. Final object is memoized in an external file to prevent needless recalculation

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
# Creating the class for put option investing

class PutInvest:
    
    # Contructor
    def __init__(self, maxrec = - 0.5, minychnge = 40, maxychnge = -20, maxPEchnge = -10, update_interval = 30):
        self.maxrec = maxrec # maximum analyst recommendation
        self.minychnge = minychnge # either the stock at least increases by min or decreases by max
        self.maxychnge = maxychnge
        self.maxPEchnge = maxPEchnge # Maximum change from trailing to forward PE
        df= pd.read_csv("ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt", sep="|")
        self.all_sym_lst =  df["Symbol"] # All tickers on the Nasdaq exchange
        self.opt = {"stocks":[], "last_updated": datetime.now()} # Tickers with options trading
        self.rec = {"stocks":[], "last_updated": datetime.now()} # Tickers with desired ratings
        self.trend = {"stocks":[], "last_updated": datetime.now()} # Tickers with desired trend
        self.fin = {"stocks":[], "last_updated": datetime.now()} # Tickers with desired financials
        self.update_interval = update_interval # Interval after which to update stocks
        self.final_suggestions = [] # Final list of suggested stocks
        
    # Function to update stocks with options
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
        
    # Function to find stocks with desired trend
    def update_trend(self):
        temp_trend = []
        if(self.opt["stocks"] == []):
            self.update_opt_stocks()
        for i in self.opt["stocks"]:
            with HiddenPrints(): # To hide unnecessary output
                data = yf.download(i,period = "1y")
            temp = data.rolling(7).mean() # Calculating rolling mean
            temp.drop(temp.index[0:6],inplace = True)
            y_chng = perchange(temp["Adj Close"][0], temp["Adj Close"][-1]) # Change over the year
            if((y_chng > self.minychnge) or (y_chng < self.maxychnge)):
                print("Adding ",i," to trend stocks")
                temp_trend.append(i)
        self.trend["stocks"] = temp_trend
        self.trend["last_updated"] = datetime.now()
        
    # Function to find stocks with desired recommendations
    def update_rec(self):
        temp_recs = []
        if(self.trend["stocks"] == []):
            self.update_trend()
        for i in self.trend["stocks"]:
            data = yf.Ticker(i)
            try: # if recommendations don't exist, the empty property will be undefined and throw an error
                temp = data.recommendations
                if(not temp.empty):
                    print("Recommendations exists for ",i)
            except:
                print("Recommendations do not exist for ",i)
                continue
            temp["To Grade"].replace("",None,inplace = True) # changing empty strings to null so that they're dropped
            temp.dropna(inplace = True) # dropping empty values
            temp["To Grade"] = temp["To Grade"].str.lower()
            temp["To Grade"].replace(["strong buy","top pick"],"buy",inplace = True)
            temp["To Grade"].replace(["outperform","overweight","positive","market outperform","sector outperform","long-term buy", "add","peer outperform","moderate buy","accumulate","conviction buy","overperformer"],"speculative buy", inplace = True)
            temp["To Grade"].replace(["perform","equal-weight","neutral","market perform","sector perform","sector weight","in-line","peer perform","mixed","market performer","fair value",""],"hold", inplace = True)
            temp["To Grade"].replace(["underperform","underweight","negative","market underperform","sector underperform","long-term sell","reduce","peer underperform","moderate sell","weak hold","conviction sell","underperformer"],"speculative sell", inplace = True)
            temp["To Grade"].replace(["strong sell","bottom pick"],"sell",inplace = True)
            temp.replace({'To Grade' : { 'buy' : 1.5, 'speculative buy' : 0.75, 'hold' : 0, 'speculative sell' : -0.75, 'sell' : -1.5}},inplace = True)
            try:
                rec = temp["To Grade"].mean()
                if(rec<self.maxrec):
                    print("Adding ",i," to analyst recommendation stocks")  
                    temp_recs.append(i)
            except:
                print("Error with symbol ",i)
        self.rec["stocks"] = temp_recs
        self.rec["last_updated"] = datetime.now()
        
    # Function to find stocks with desired financials
    def update_fin(self):
        temp_fin = []
        if(self.trend["stocks"] == []):
            self.update_trend()
        for i in self.trend["stocks"]:
            data = yf.Ticker(i)
            temp = data.info
            temp_keys = list(temp.keys()) # Getting a list of what information about the stock is available
            if(("forwardPE" in temp_keys) and (("trailingPE" in temp_keys) or ("priceToSalesTrailing12Months" in temp_keys))): # We can substitute Trailing PE with Trailing Price Sales ratio
                if("trailingPE" in temp_keys):
                    chnge = perchange(temp["trailingPE"],temp["forwardPE"])
                    if(chnge < self.maxPEchnge):
                        print("Adding ticker ",i, "to financial stocks")
                        temp_fin.append(i)
                else:
                    chnge = perchange(temp["priceToSalesTrailing12Months"],temp["forwardPE"])
                    if(chnge < self.maxPEchnge):
                        print("Adding ticker ",i, "to financial stocks")
                        temp_fin.append(i)
        self.fin["stocks"] = temp_fin
        self.fin["last_updated"] = datetime.now()
    
    # Function to update outdated information
    def check_for_updates(self):
        if(((datetime.now() - self.fin["last_updated"]).days) >= self.update_interval):
            self.update_fin()
        if(((datetime.now() - self.rec["last_updated"]).days) >= self.update_interval):
            self.update_rec()
        self.final_suggestions = set(self.fin["stocks"])&set(self.rec["stocks"])
    
    # Function to return the final list of suggested stocks
    def get_suggestions(self): 
        return self.final_suggestions
    
    # Function to store the object in an external file for future efficiency
    def memo(self): 
        with open('memoPut.dictionary', 'wb') as memo_dictionary_file:
            pickle.dump(self, memo_dictionary_file)
            print("object memoized!")


#%%
# Example to use the above class

with open('memoPut.dictionary', 'rb') as memo_dictionary_file: # Checking if an object has already been memoized
    obj = pickle.load(memo_dictionary_file)
    
if(obj.get_suggestions()==[]): # If the extracted object is empty, then a new object is created and memoized 
    obj = PutInvest()
    obj.check_for_updates()
    obj.get_suggestions()
    obj.memo()
else:
    obj.get_suggestions()    
