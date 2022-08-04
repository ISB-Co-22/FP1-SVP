from pydoc import describe
import pandas as pd
import requests as httpRequest
from scrapy import Selector
import openpyxl

# Base URL for TickerTape
tickertape_baseUrl = "https://tickertape.in"

# Relative URL for TickerTape Individual Stock News with {0} as placeholder for Stock Code
tickertape_PageStockurlSuffix = "{0}/news?checklist=basic&type=news"

# Api (FHR) URL for Individual Stock News on TickerTape. Count and Offset represent no. of news items to fetch and no. of items to skip
tickertape_ApiStockNewsUrl = "https://api.tickertape.in/stocks/feed/{0}?count=100&offset=0&types=news-article,opinion-article"

# Get the html content for the TickerTape Nifty 50 Stock List URL to extract the metadat for each stock
tickertapedotcom_stockList = httpRequest.get("https://www.tickertape.in/indices/nifty-50-index-.NSEI/constituents").content
sel_tickertape = Selector(text = tickertapedotcom_stockList)

# Get Relative URL link for each stock as list
stockSeedList_Links = sel_tickertape.xpath('//h5/a[starts-with(@href, "/stocks")]/@href').extract()

# Get Relative URL link for each stock Metadata i.e FullName | Stock Unique Code | Stock Internal Code
stockSeedList_Names = sel_tickertape.xpath('//h5/a[starts-with(@href, "/stocks")]/@title').extract()

# Create a dataframe with columns to capture all the Stock Metadata
df_StockListMetadata = pd.DataFrame({"Stock_FullName": [], "Stock_Code": [] , "Sector": [],"TickerTapePageUrl" : [], "TickerTapeApiUrl" : [], "InvestingUrl" : []})

# Iterate through the lists created above to populate the Dataframe with Stock Name, Code, News Page URL, News API URL for each Stock
for (stockName, stockLink) in zip(stockSeedList_Names, stockSeedList_Links):
    df_StockListMetadata = df_StockListMetadata.append({
                                    'Stock_FullName' : str.split(stockName, "|")[0],
                                    'Stock_Code' : str.split(stockName, "|")[1],
                                    'Sector' : str.split(stockName, "|")[2], 
                                    'TickerTapePageUrl' :  tickertape_baseUrl + tickertape_PageStockurlSuffix.replace('{0}', stockLink),
                                    'TickerTapeApiUrl' : tickertape_ApiStockNewsUrl.replace('{0}', stockLink[stockLink.rindex("-")+1:])},  ignore_index = True)
df_StockListMetadata.to_csv("StockMetadata.csv")





