# -*- coding: utf-8 -*-
"""
Created on Fri Mar 19 22:08:08 2021

@author: emota
"""

#%%

import os
import yfinance
import pandas as pd
import numpy as np
from pathlib import Path
from six import iteritems
from datetime import datetime
#%%

import trading_calendars as tc

#%%

tsx = tc.get_calendar("XTSE")

#%%
show_progress = True

home = str(Path.home()) + "/"
path = home + "your_data_file.zip"
column_names = ["symbol",
                "date",
                "unadjusted_open",
                "unadjusted_high",
                "unadjusted_low",
                "unadjusted_close",
                "unadjusted_volume",
                "dividends", "splits",
                "adjusted_open",
                "adjusted_high",
                "adjusted_low",
                "adjusted_close",
                "adjusted_volume"]
#%%

with open("portfolio/TSX.txt", "r") as f:
    file_raw = f.readlines()
    
#%%

sectors = {}
fails = []
parsed = []

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
    
    
#%%

tick = yfinance.Ticker("DCBO.TO")

#%%

d= tick.history(start='2016-01-01', end='2021-03-19', interval='1d')


#%%

print(d.index.max())

#%%
print(d.columns)

#%%

valid_days = tsx.sessions_in_range(d.index.min(), d.index.max())

#%%
print(d.dtypes)
print(d.index)
print(valid_days)

#%%
d.index=d.index.tz_localize(tz="UTC")
print(d.index)
#%%
print(tsx.previous_close(d.index.max()) - pd.DateOffset(hours=20))
#%%
print(d[d.index == tsx.previous_close(d.index.max()) - pd.DateOffset(hours=20)])

#%%

def load_data_table(show_progress=show_progress):

    
    stocks = None
    i = 0
    
    with open("portfolio/TSX.txt", "r") as f:
        file_raw = f.readlines()
        
    total = len(file_raw) - 1
        
    for line in file_raw[1:]:
        ticker = line.split()[0].strip()
        tick = yfinance.Ticker(ticker)
        
        data = tick.history(start='2016-01-01', end='2021-03-19', interval='1d')
        
        i += 1
        if len(data.index) == 0:
            continue
        data.index=data.index.tz_localize(tz="UTC")
        
        
        data_s = data.copy()
        
        data_s.rename(columns={
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume',
            'Dividends': 'dividends',
            'Stock Splits': 'split_ratio'
        }, inplace=True, copy=False)
        
        data_s.index.rename('date', inplace=True)
        #print(data_s.head())
        valid_days = tsx.sessions_in_range(data_s.index.min(), data_s.index.max())
        data_s = data_s[data_s.index.isin(valid_days)]
        #print(data_s.head())
        missing_dates = valid_days[valid_days.isin(data_s.index) == False]
        b = False
        for d in missing_dates:
            prev_d = tsx.previous_close(d).replace(hour=0, minute=0, second=0)
            tmp = data_s[data_s.index == prev_d].copy()
            
            tmp.rename(index={prev_d:d},inplace=True)
            
            data_s = data_s.append(tmp)
            #print(data_s[data_s.index == d])
            #if ticker == "ALYA.TO":
            #    b = True
            #    print(prev_d)
            #    print(tmp)
            #    print(len(data_s))
        #print(data_s.head())
        #break
        data_s = data_s[~data_s.index.duplicated()]
        try:
            data_s.to_csv(f"Portfolio/daily/{ticker}.csv")
        except:
            continue
        
        if b:
            break
        
        if show_progress:
            print(round((i*100)/total,2))
        
        continue
        data['symbol'] = ticker
        
        
        """
        df_na = data.dropna(how='all')
        
        if df_na["Close"].iloc[-1] > 20:
            continue
        elif df_na['Close'].iloc[-1] < 1:
            continue"""
        
        if stocks is None:
            stocks = data
        else:
            stocks = pd.concat([stocks, data])
        
        
        
        
    return None
    stocks.rename(columns={
        'Date': 'date',
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume',
        'Dividends': 'dividends',
        'Stock Splits': 'split_ratio'
    }, inplace=True, copy=False)

    return stocks


#%%

s = load_data_table(True)

#%%

s.to_csv("Portfolio/historical_5_year_data.csv")


#%%

def gen_asset_metadata(data, show_progress):

    data = data.groupby(
        by='symbol'
    ).agg(
        {'date': [np.min, np.max]}
    )
    data.reset_index(inplace=True)
    data['start_date'] = data.date.amin
    data['end_date'] = data.date.amax
    del data['date']
    data.columns = data.columns.get_level_values(0)
    data['auto_close_date'] = data['end_date'].values + pd.Timedelta(days=1)

    return data

def parse_splits(data, show_progress):

    data['split_ratio'] = 1.0 / data.split_ratio
    data.rename(
        columns={
            'split_ratio': 'ratio',
            'date': 'effective_date',
        },
        inplace=True,
        copy=False,
    )

    return data

def parse_dividends(data, show_progress):

    data['record_date'] = data['declared_date'] = data['pay_date'] = pd.NaT
    data.rename(columns={'date': 'ex_date',
                         'dividends': 'amount'}, inplace=True, copy=False)
    return data

def parse_pricing_and_vol(data,
                          sessions,
                          symbol_map):
    for asset_id, symbol in iteritems(symbol_map):
        asset_data = data.xs(
            symbol,
            level=1
        ).reindex(
            sessions.tz_localize(None)
        ).fillna(0.0)
        yield asset_id, asset_data

def ingest(environ,
           asset_db_writer,
           minute_bar_writer,
           daily_bar_writer,
           adjustment_writer,
           calendar,
           start_session,
           end_session,
           cache,
           show_progress,
           output_dir):
    raw_data = load_data_table(path, show_progress=show_progress)
    asset_metadata = gen_asset_metadata(
        raw_data[['symbol', 'date']],
        show_progress
    )
    asset_db_writer.write(asset_metadata)
    symbol_map = asset_metadata.symbol
    sessions = calendar.sessions_in_range(start_session, end_session)
    raw_data.set_index(['date', 'symbol'], inplace=True)
    daily_bar_writer.write(
        parse_pricing_and_vol(
            raw_data,
            sessions,
            symbol_map
        ),
        show_progress=show_progress
    )
    raw_data.reset_index(inplace=True)
    raw_data['symbol'] = raw_data['symbol'].astype('category')
    raw_data['sid'] = raw_data.symbol.cat.codes
    adjustment_writer.write(
        splits=parse_splits(
            raw_data[[
                'sid',
                'date',
                'split_ratio',
            ]].loc[raw_data.split_ratio != 1],
            show_progress=show_progress
        ),
        dividends=parse_dividends(
            raw_data[[
                'sid',
                'date',
                'dividends',
            ]].loc[raw_data.dividends != 0],
            show_progress=show_progress
        )
    )
    
    
    #%%
    
with open("Portfolio/daily/ALA.TO.csv", "r") as f:
    ts = f.readlines() 
    
    
    #%%

ts = pd.read_csv("Portfolio/daily/ALYA.TO.csv", parse_dates=['date']) 


#%%

if len(ts) == 0:
    print("Nothing")
    
#%%

valid_days = tsx.sessions_in_range(ts.date.min(), ts.date.max())

    #%%
    
vd = valid_days.to_list()

#%%

ts = ts[~ts.date.duplicated(keep='first')]

#%%

missing_dates = valid_days[valid_days.isin(ts.date) == False]

#%%

extra_dates = ts[ts.date.isin(valid_days) == False]

#%%%
print(ts.head())

#%%
print(missing_dates)


#%%


for d in missing_dates:
    prev_d = tsx.previous_close(d) - pd.DateOffset(hours=21)
    tmp = ts[ts.date == prev_d].copy()
    print(tmp)
    tmp.date = d
    ts = ts.append(tmp).reset_index()
    
#%%

print(prev_d)
    
    #%%%
print(ts[ts.date == d])
#%%    
print(ts[ts.date == prev_d])
#%%

da = ts.date.to_list()