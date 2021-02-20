# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 09:39:33 2021

@author: emota
"""

#%%

import joblib
import pandas as pd
import numpy as np
import yfinance as yf
import seaborn as sns
import scipy.stats as scs
import statsmodels.api as sm
import statsmodels.tsa.api as smt
import matplotlib as plt

#%%

def plotAutoccorelation(df, ticker):
    N_LAGS = 50
    SIGNIFICANCE_LEVEL = 0.05
    df = df.dropna()
    acf = smt.graphics.plot_acf(df.log_rtn, lags=N_LAGS, alpha=SIGNIFICANCE_LEVEL)

#%%

with open("stock_directory.jbl", 'rb') as f:
    stock_directory = joblib.load(f)

#%%

for ticker, stock in stock_directory.items():
    path = stock["main_df_path"]
    with open(path, "rb") as f:
        df = joblib.load(f)
        plotAutoccorelation(df, ticker)