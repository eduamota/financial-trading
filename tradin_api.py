
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import pandas as pd
import numpy as np
import threading
import time
import os
from datetime import datetime, timedelta
#%%

class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.daily_data = []
        self.id = 0
        
    def tickPrice(self, reqId, tickType, price, attrib):
        if tickType == 2 and reqId == 1:
            print('The current ask price is: ', price)
    
    def historicalData(self, reqId, bar):
            
        data = [bar.date, bar.open, bar.close, bar.low, bar.high]
        self.daily_data.append(data)
        
    def getNextID(self):
        self.id += 1
        return self.id
    
    def saveDailyDate(self, stock, date):
        if len(self.daily_data) == 0:
            return False
        df = pd.DataFrame (self.daily_data, columns=['date', "open", "close", "low", "high"])
        if not os.path.exists("data"):
            os.mkdir("data")
        if not os.path.exists(f"data/{stock}"):
            os.mkdir(f"data/{stock}")
        df.to_csv (f"data/{stock}/{date}.csv", index = False, header=True)
        self.daily_data = []
        
            
    def getHistoricalData(self, stock, date):
        stock_contract = Contract()
        stock_contract.symbol = stock
        stock_contract.secType = 'STK'
        stock_contract.exchange = 'SMART'
        stock_contract.currency = 'CAD'
        
        app.reqHistoricalData(self.getNextID(), stock_contract, date, '1 D', '1 min', 'BID', 0, 1, False, [])

def run_loop():
	app.run()
#%%
app = IBapi()
app.connect('127.0.0.1', 7496, 123)

#Start the socket in a thread
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()

#%%
stocks = ["MAX", "LAC", "SBB", "AMM", "WM"]

#%%
for stock in stocks:
    today = datetime.now()
    begin = today - timedelta(days=60)
    get_date = begin
    while get_date <= today:
        date = get_date.strftime("%Y%m%d")
        app.getHistoricalData(stock, f"{date} 23:59:59")
        time.sleep(2)
        app.saveDailyDate(stock, date)
        get_date = get_date + timedelta(days=1)

#%%
app.disconnect()
api_thread.join()

#%%

daily = app.daily_data