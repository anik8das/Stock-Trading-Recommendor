"""
Value Investing Recommendor

Stocks are checked for:
    1. Market Cap: At least 100B 
    2. Analyst Ratings: At least be an outperform on average
    3. Yearly change: At least up 25% over the last year
    4. Country: Chinese stocks are avoided due to unreliability
    5. Dollar volume: At least 500 million
    6. Suggested stocks are updated every 30 days
    7. The parameters can be changed through the constructor
    8. Final object is memoized in an external file to prevent needless recalculation

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
# Creating the class for value investing

class ValueInvest:
    
    # Contructor
    def __init__(self, minrec = 0.5, minychnge = 25, minmc = 50000000000, mindv = 500000000, update_interval = 30):
        self.minrec = minrec # Minimum threshold for recommendation
        self.minychnge = minychnge # Minimum gain over the last year
        self.minmc = minmc # Minimum market cap
        self.mindv = mindv # Minimum dollar volume
        df= pd.read_csv("ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt", sep="|")
        self.all_sym_lst = df["Symbol"] # List containing the symbols of every stock on Nasdaq
        self.rec = {"stocks":[], "last_updated": datetime.min} # Objects containing information for recommendation, trend, and financial symbols
        self.fin = {"stocks":[], "last_updated": datetime.min}
        self.trend = {"stocks":{}, "last_updated": datetime.min}
        self.update_interval = update_interval # Interval at which stocks are updated
        self.final_suggestions = [] # List containing final suggestions
        
    # Function to update the class
    def check_for_updates(self):
        if(((datetime.now() - self.trend["last_updated"]).days) >= self.update_interval):
            self.update_trend()
        if(((datetime.now() - self.rec["last_updated"]).days) >= self.update_interval):
            self.update_rec()
        if(((datetime.now() - self.fin["last_updated"]).days) >= self.update_interval):
            self.update_fin()
        self.final_suggestions = set(list(self.trend["stocks"].keys()))&set(self.rec["stocks"])&set(self.fin["stocks"])
    
    # Function to update desired trend following stocks
    def update_trend(self):
        temp_trend = {}        
        for i in self.all_sym_lst:
            with HiddenPrints():
                data = yf.download(i,period = "1y")
            temp = data.rolling(14).mean()
            temp.drop(temp.index[0:13],inplace = True)
            pot = perchange(temp["Adj Close"].max(),temp["Adj Close"][-1])
            y_chng = perchange(temp["Adj Close"][0], temp["Adj Close"][-1])
            if(y_chng > self.minychnge):
                print("Adding ",i," to trend stocks")
                temp_trend[i] = pot
        self.trend["stocks"] = temp_trend
        self.trend["last_updated"] = datetime.now()
        
    # Function to update recommended stocks
    def update_rec(self):
        temp_recs = []
        lst = self.all_sym_lst if (list(self.trend.stocks.keys()) == []) else list(self.trend.stocks.keys())
        for i in lst:
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
                if(rec>self.minrec):
                    print("Adding ",i," to analyst recommendation stocks")  
                    temp_recs.append(i)
            except:
                print("Error with symbol ",i)
        self.rec["stocks"] = temp_recs
        self.rec["last_updated"] = datetime.now()
        
    # Function to update stocks satisfying financial requirements
    def update_fin(self):
        temp_fin = []
        lst = (self.all_sym_lst if (list(self.trend["stocks"].keys()) == []) else list(self.trend["stocks"].keys())) if self.rec['stocks']==[] else self.rec['stocks']
        for i in lst:
            data = yf.Ticker(i)
            temp = data.info
            cntry = temp["country"].lower()
            mc = int(temp["marketCap"])
            dolvol = float(temp["volume"])*float(temp["previousClose"])
            if((dolvol < 500000000) or (mc < 50000000000) or (cntry == "china")):
                continue
            print("Adding ",i," to financially strong stocks")
            temp_fin.append(i)
        self.fin["stocks"] = temp_fin
        self.fin["last_updated"] = datetime.now()
    
    # Function to return the final list of suggested stocks
    def get_suggestions(self): 
        return self.final_suggestions
    
    # Function to store the object in an external file for future efficiency
    def memo(self): 
        with open('memoValue.dictionary', 'wb') as memo_dictionary_file:
            pickle.dump(self, memo_dictionary_file)
            print("object memoized!")
            
        
#%%
# Example to use the above class

with open('memoValue.dictionary', 'rb') as memo_dictionary_file: # Checking if an object has already been memoized
    obj = pickle.load(memo_dictionary_file)
    
if(obj.get_suggestions()==[]): # If the extracted object is empty, then a new object is created and memoized 
    obj = ValueInvest()
    obj.check_for_updates()
    obj.get_suggestions()
    obj.memo()
else:
    obj.get_suggestions()
