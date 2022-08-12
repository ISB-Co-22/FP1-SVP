import pandas as pd
from nsepy import get_history
from datetime import date
from datetime import datetime
from datetime import timedelta
import string as str


def GetStockPriceMetrics(mode, startDate, endDate, stockCode = ''):
    # Setting Start Date as 6 days behind to ensure the MA5 and ROC values are valid for the original Start Date
    startDate = startDate - timedelta(days=6)
    endDate = endDate + timedelta(days=1)
    df = []
    df = pd.DataFrame(df)
    df1 = df
    counter = 0
    if (mode == 'Prediction'):
        df = get_history(symbol=stockCode,start=startDate, end= endDate)
        df1 = df.drop(['Series','Prev Close','High','Low','Last','VWAP','Volume','Turnover', 'Trades', 'Deliverable Volume', '%Deliverble'], axis = 1)
        df1['MA5'] = df1['Close'].rolling(window = 5).mean()
        df1['ROC'] = (df1['MA5']-df1['Close'])/df1['MA5']
        df1['ROC_10x'] = df1['ROC'] * 10
        df1.rename(columns = {'Symbol': 'Stock_Code'}, inplace=True)
        df1.reset_index(inplace = True)
        return df1.iloc[-1:]
    else :
        symbol = ['TATACONSUM','TITAN','HINDUNILVR','TATAMOTORS','LT','MARUTI','HDFC','EICHERMOT','NESTLEIND','M&M','BPCL','BRITANNIA','BHARTIARTL','CIPLA','BAJFINANCE','ASIANPAINT','ULTRACEMCO','BAJAJ-AUTO','SBILIFE','NTPC','ITC','HDFCBANK','KOTAKBANK','BAJAJFINSV','SHREECEM','APOLLOHOSP','COALINDIA','ADANIPORTS','HINDALCO','GRASIM','HDFCLIFE','INFY','HEROMOTOCO','RELIANCE','UPL','TCS','TECHM','DIVISLAB','ICICIBANK','SBIN','SUNPHARMA','INDUSINDBK','ONGC','AXISBANK','DRREDDY','JSWSTEEL','WIPRO','HCLTECH','POWERGRID','TATASTEEL'
        ]
        counter = 0
        for i in symbol:
            data = get_history(symbol=i,start=startDate, end= endDate)
            data = pd.DataFrame(data)
            df = pd.concat([df,data])
            df1 = df.drop(['Series','Prev Close','High','Low','Last','VWAP','Volume','Turnover', 'Trades', 'Deliverable Volume', '%Deliverble'], axis = 1)
            df1['MA5'] = df1['Close'].rolling(window = 5).mean()
            df1['ROC'] = (df1['MA5']-df1['Close'])/df1['MA5']
            df1['ROC_10x'] = df1['ROC'] * 10
            # Add a column (Y) as the relative increae or decrease from todays closing price to next day's opening Price. This is required for training the model
            df1['Prediction'] = (df1['Open'].shift(-1) - df1['Close']) / df1['Close']
            df1.rename(columns = {'Symbol': 'Stock_Code'}, inplace=True)
            df1.reset_index(inplace = True)
        return df1