# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 12:11:58 2021

@author: emota
"""

#%%

import pandas as pd
import numpy as np
import yfinance as yf
import os
import joblib
from os import path
from datetime import datetime
#%%

stock = 'PYPL'

df = yf.download(stock,
                 start='2020-06-01',
                 end='2021-02-18'
                 )

#%%

df = df.loc[:, ['Adj Close']]
df.rename(columns={'Adj Close':'adj_close'}, inplace=True)

#%%

df['simple_rtn'] = df.adj_close.pct_change()
df['log_rtn'] = np.log(df.adj_close/df.adj_close.shift(1))

#%%

p = f"portfolio/{stock}"

if not path.exists(p):
    os.mkdir(p)

#%%

with open(f"{p}/{stock}_raw.jbl", 'wb') as f:
    joblib.dump(df, f)
    
#%%

stock_directory = {}
    
try:
    with open("stock_directory.jbl", "rb") as f:
        stock_directory = joblib.load(f)
except:
    pass

#%%

if stock not  in stock_directory:
    stock_directory[stock] = {}


stock_directory[stock]['last_update'] = datetime.now()

stock_directory[stock]['log_return'] = True
stock_directory[stock]['simple_return'] = True
stock_directory[stock]['main_df_path'] = f"{p}/{stock}_raw.jbl"


with open("stock_directory.jbl", "wb") as f:
    joblib.dump(stock_directory, f)

#%%    