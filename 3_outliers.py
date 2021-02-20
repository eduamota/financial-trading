# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 16:13:03 2021

@author: emota
"""

#%%

import pandas as pd
import numpy as np
import joblib
import matplotlib as plt

#%%

with open("stock_directory.jbl", "rb") as f:
    stock_directory = joblib.load(f)

#%%

def idOutliers(row, n_sigmas=3):
    x = row['simple_rtn']
    mu = row['mean']
    sigma = row['std']
    
    if (x > mu + 3 * sigma) | (x < mu - 3 * sigma):
        return 1
    else:
        return 0

def identifyOutliers(data):
    data_rolling = data[['simple_rtn']].rolling(window=21).agg(['mean', 'std'])
    
    data_rolling.columns = data_rolling.columns.droplevel()
    
    data_outliers = data.join(data_rolling)
    data_outliers['outlier'] = data_outliers.apply(idOutliers, axis=1)
    
    outliers = data_outliers.loc[data_outliers['outlier'] ==1, ['simple_rtn']]
    return data_outliers, outliers


def plotStock(data, outliers, ticker):
    
    fig, ax = plt.pyplot.subplots()
    
    ax.plot(data.index, data.simple_rtn, color='blue', label='Normal')
    
    ax.scatter(outliers.index, outliers.simple_rtn, color='red', label='Anomaly')
    ax.set_title(f"{ticker} stock returns")
    ax.legend(loc='lower right')


#%%    

for ticker, stock in stock_directory.items():
    path = stock['main_df_path']
    with open(path, "rb") as f:
        data = joblib.load(f)
    data, outliers = identifyOutliers(data)
    plotStock(data, outliers, ticker)