import json
import openpyxl
import pandas as pd
import requests as httpRequest
from scrapy import Selector

# Base URL for TickerTape
tickertape_baseUrl = "https://tickertape.in"

# Relative URL for TickerTape Individual Stock News with {0} as placeholder for Stock Code
tickertape_PageStockurlSuffix = "{0}/news?checklist=basic&type=news"

# Api (FHR) URL for Individual Stock News on TickerTape. Count and Offset represent no. of news items to fetch and no. of items to skip
tickertape_ApiStockNewsUrl = "https://api.tickertape.in/stocks/feed/{0}?count=10&offset=0&types=news-article,opinion-article"

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
                                    'Stock_FullName' : str.split(stockName, "|")[0].strip(),
                                    'Stock_Code' : str.split(stockName, "|")[1].strip(),
                                    'Sector' : str.split(stockName, "|")[2].strip(), 
                                    'TickerTapePageUrl' :  tickertape_baseUrl + tickertape_PageStockurlSuffix.replace('{0}', stockLink),
                                    'TickerTapeApiUrl' : tickertape_ApiStockNewsUrl.replace('{0}', stockLink[stockLink.rindex("-")+1:])},  ignore_index = True)

# Dataframe to hold every news artcile with datetime and Stock name etc
df_DateWiseStockNews = []

# Iterate through every stock in the Metadata DF and fetch the news using the stock specific URL
for eachStockIndex in df_StockListMetadata.index :
    # Get response having news article for each stock
    response_text = httpRequest.get(df_StockListMetadata['TickerTapeApiUrl'][eachStockIndex]).text
    # Remove the starting to only only the news article
    response_text = response_text[response_text.index("["):-2]
    # Parse the JSON into a temporary dataframe
    df_Temp = pd.json_normalize(json.loads(response_text))
    # Copy over the Stock code and name from the metadata DF into the temp DF to associate every news item with Stock
    df_Temp["Stock_Code"] = df_StockListMetadata['Stock_Code'][eachStockIndex]
    df_Temp["Stock_Name"] = df_StockListMetadata['Stock_FullName'][eachStockIndex]
    # Drop the unused columns
    df_Temp = df_Temp.drop(['feed_type', 'link', 'image', '_id' , 'publisher.logo', 'publisher.id', 'publisher.name'], axis = 1)
    if (eachStockIndex == 0):
        # Copyover the schema of temp DF to final DF to allow merging / concat of dataframes
        df_DateWiseStockNews = df_Temp
    else:
        df_DateWiseStockNews = pd.concat([df_DateWiseStockNews, df_Temp])
df_DateWiseStockNews.to_csv("StockNewsData.csv")
df_StockListMetadata.to_csv("StockMetaData.csv")