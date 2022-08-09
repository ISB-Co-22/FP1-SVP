import pandas as pd
from nsepy import get_history
from datetime import date

symbol = ['TATACONSUM','TITAN','HINDUNILVR','TATAMOTORS','LT','MARUTI','HDFC','EICHERMOT','NESTLEIND','M&M','BPCL','BRITANNIA','BHARTIARTL','CIPLA','BAJFINANCE','ASIANPAINT','ULTRACEMCO','BAJAJ-AUTO','SBILIFE','NTPC','ITC','HDFCBANK','KOTAKBANK','BAJAJFINSV','SHREECEM','APOLLOHOSP','COALINDIA','ADANIPORTS','HINDALCO','GRASIM','HDFCLIFE','INFY','HEROMOTOCO','RELIANCE','UPL','TCS','TECHM','DIVISLAB','ICICIBANK','SBIN','SUNPHARMA','INDUSINDBK','ONGC','AXISBANK','DRREDDY','JSWSTEEL','WIPRO','HCLTECH','POWERGRID','TATASTEEL'
]
df= []
df = pd.DataFrame(df)
counter = 0
for i in symbol:
    data = get_history(symbol=i,start=date(2022,7,20), end= date(2022,8,8))
    data = pd.DataFrame(data)
    df = pd.concat([df,data])
df1 = df.drop(['Series','Prev Close','High','Low','Last','VWAP','Volume','Turnover', 'Trades', 'Deliverable Volume', '%Deliverble'], axis = 1)
df1['MA5'] = df1['Close'].rolling(window = 5).mean()
df1['ROC'] = (df1['MA5']-df1['Close'])/df1['MA5']
df1['Result(Y)'] = (df1['Open'].shift(-1) - df1['Close']) / df1['Close']