# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 08:57:55 2021

@author: emota
"""

#%%

import os
import yfinance
import pandas as pd

#%%

with open("portfolio/TSX.txt", "r") as f:
    file_raw = f.readlines()
    
#%%

sectors = {}
fails = []
parsed = []
ticker_sector = []
total = len(file_raw)
i = 0
for line in file_raw[1:]:
    ticker = line.split()[0].strip()
    tick = yfinance.Ticker(ticker)
    try:
        ticker_info = tick.info
        parsed.append(ticker)
    except:
        fails.append(ticker)
        continue
    sector = "unkown"
    if "sector" in ticker_info:    
        sector = ticker_info['sector']
        
    if sector not in sectors:
        sectors[sector] = []
        
    sectors[sector].append(ticker)
    ticker_sector.append({"symbol":ticker, "sector":sector})
    
#%%

import joblib

joblib.dump(df, "symbol-sector.jbl")


#%%
df = pd.DataFrame(ticker_sector)

#%%

print(df.head())

#%%

sectors = df.sector.unique()


#%%

sectors = pd.DataFrame(sectors, columns=['sector'])

#%%

print(sectors.head())

#%%

sectors.index.name = 'index'

#%%
sectors.to_csv("sectors.csv")

#%%

df.to_csv("symbols_sectors.csv", index=False)


#%%

def map_sector(row):
    inx = sectors[sectors.sector == row.sector].index.values[0]
    row['sector_id'] = inx
    
    return row
    
#%%
    

mapped = df.apply(map_sector, axis=1)

#%%

print(mapped.head(20))

#%%

print(sectors.index.values)