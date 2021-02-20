# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 17:38:53 2020

@author: emota
"""

#%%

import pandas as pd 
import yfinance as yf

#%%

df_yahoo = yf.download('LAC.TO', 
                       start='2010-01-01', 
                       end='2020-09-18',
                       progress=False)

#%%

import pandas as pd
import seaborn as sns
from fbprophet import Prophet

#%%

df = df_yahoo.copy()
#%%
df.reset_index(drop=False, inplace=True)
df.rename(columns={'Date': 'ds', 'Close': 'y'}, inplace=True)

#%%

train_indices = df.ds.apply(lambda x: x.year) < 2018
df_train = df.loc[train_indices].dropna()
df_test = df.loc[~train_indices].reset_index(drop=True)

#%%
model_prophet = Prophet(seasonality_mode='additive')
model_prophet.add_seasonality(name='monthly', period=30.5, 
                              fourier_order=5)
model_prophet.fit(df_train)

#%%

df_future = model_prophet.make_future_dataframe(periods=365)
df_pred = model_prophet.predict(df_future)
model_prophet.plot(df_pred)

#%%

!pip install fbprophet