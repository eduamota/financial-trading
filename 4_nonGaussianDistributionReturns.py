# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 09:10:16 2021

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

def plotGaussian(df, ticker):
    r_range = np.linspace(min(df.log_rtn), max(df.log_rtn), num=1000)

    mu = df.log_rtn.mean()
    sigma = df.log_rtn.std()
    norm_pdf = scs.norm.pdf(r_range, loc=mu, scale=sigma)
    
    fig, ax = plt.pyplot.subplots(1, 2, figsize=(16, 8))
    sns.distplot(df.log_rtn, kde=False, norm_hist=True, ax=ax[0])
    ax[0].set_title(f'Distrinbution of {ticker} returns', fontsize=16)
    ax[0].plot(r_range, norm_pdf, 'g', lw=2, label=f'N({mu:.2f}, {sigma**2:.4f})')
    ax[0].legend(loc='upper left')
    
    #Q-Q plot
    
    qq = sm.qqplot(df.log_rtn.values, line='s', ax=ax[1])
    ax[1].set_title('Q-Q plot', fontsize=16)
    
    plt.pyplot.show()

#%%

with open("stock_directory.jbl", 'rb') as f:
    stock_directory = joblib.load(f)

#%%

for ticker, stock in stock_directory.items():
    path = stock["main_df_path"]
    with open(path, "rb") as f:
        df = joblib.load(f)
        plotGaussian(df, ticker)

#%%


