# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 15:50:25 2021

@author: emota
"""

#%%
import joblib
import matplotlib as plt
import pandas as pd
import numpy as np

#%%

with open("stock_directory.jbl", "rb") as f:
    stock_directory = joblib.load(f)
    
#%%

def plotStock(data, ticker):
    
    fig, ax = plt.pyplot.subplots(3, 1, figsize=(24, 20), sharex=True)
    
    data.adj_close.plot(ax=ax[0])
    ax[0].set(title = f'{ticker} time series', ylabel = 'Stock price ($)')
    
    data.simple_rtn.plot(ax=ax[1])
    ax[1].set(ylabel = 'Simple returns (%)')

    data.log_rtn.plot(ax=ax[2])
    ax[2].set(xlabel = 'Date', ylabel = 'Log retursn (%)')

#%%

for ticker, stock in stock_directory.items():
    path = stock['main_df_path']
    with open(path, "rb") as f:
        data = joblib.load(f)
    plotStock(data, ticker)
    
#%%
    
import cufflinks as cf
from plotly.offline import iplot, init_notebook_mode

#%% 

#cf.set_config_file(world_readable=True, theme='pearl', offline=True) 
#init_notebook_mode(False)
#%%

data.iplot(subplots=True, shape=(3,1), shared_xaxes=True, title='PYPL time series')  