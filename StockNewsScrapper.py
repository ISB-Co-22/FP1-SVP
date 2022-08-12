import json
import openpyxl
import pandas as pd
import requests as httpRequest
from scrapy import Selector
import flair as fl

sentiment_model = fl.models.TextClassifier.load('en-sentiment')

def GetTickerTapeNewsSentiment(mode, stockCode = ''):
    # Base URL for TickerTape
    tickertape_baseUrl = "https://tickertape.in"

    # Relative URL for TickerTape Individual Stock News with {0} as placeholder for Stock Code
    tickertape_PageStockurlSuffix = "{0}/news?checklist=basic&type=news"

    # Api (FHR) URL for Individual Stock News on TickerTape. Count and Offset represent no. of news items to fetch and no. of items to skip
    if (mode == 'Prediction'):
        tickertape_ApiStockNewsUrl = "https://api.tickertape.in/stocks/feed/{0}?count=3&offset=0&types=news-article,opinion-article"
    else:
        tickertape_ApiStockNewsUrl = "https://api.tickertape.in/stocks/feed/{0}?count=30&offset=0&types=news-article,opinion-article"


    # Get the html content for the TickerTape Nifty 50 Stock List URL to extract the metadata for each stock
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

    if (mode == 'Prediction'):
        # Fetch News article for the stock to predict using API
        df_stock = df_StockListMetadata[df_StockListMetadata['Stock_Code'] == stockCode]
        str_url = df_stock['TickerTapeApiUrl'].tolist()[0]
        response_text = httpRequest.get(str_url).text
        # Remove the starting to only only the news article
        response_text = response_text[response_text.index("["):-2]
        # Parse the JSON into a temporary dataframe
        df_DateWiseStockNews = pd.json_normalize(json.loads(response_text))
        # Copy over the Stock code and name from the metadata DF into the temp DF to associate every news item with Stock
        df_DateWiseStockNews["Stock_Code"] = stockCode
        # Drop the unused columns
        df_DateWiseStockNews = df_DateWiseStockNews.drop(['feed_type', 'link', 'image', '_id' , 'publisher.logo', 'publisher.id', 'publisher.name', 'stocks'], axis = 1)
        # Calling the function to assign scores
        df_DateWiseStockNews = AssignSentimentScores(df_DateWiseStockNews, "title")
    else :
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
            # df_Temp["Stock_Name"] = df_StockListMetadata['Stock_FullName'][eachStockIndex]
            # Drop the unused columns
            df_Temp = df_Temp.drop(['feed_type', 'link', 'image', '_id' , 'publisher.logo', 'publisher.id', 'publisher.name', 'stocks'], axis = 1)
            # Calling the function to assign scores
            df_Temp = AssignSentimentScores(df_Temp, "title")
            if (eachStockIndex == 0):
                # Copyover the schema of temp DF to final DF to allow merging / concat of dataframes
                df_DateWiseStockNews = df_Temp
            else:
                df_DateWiseStockNews = pd.concat([df_DateWiseStockNews, df_Temp])
    # Add a new column to keep Date part only
    df_DateWiseStockNews['DateOnly'] = pd.to_datetime(df_DateWiseStockNews["date"]).dt.date
    # Aggregating Sentiment scores for every combination of StockCode and Date
    df_NewsScoreByStockNDate = df_DateWiseStockNews.groupby(['Stock_Code', 'DateOnly']).agg({'Sentiment_Score': ['mean']})
    df_NewsScoreByStockNDate = df_NewsScoreByStockNDate.reset_index()
    df_NewsScoreByStockNDate.columns = df_NewsScoreByStockNDate.columns.to_flat_index().str.join('_')
    df_NewsScoreByStockNDate.rename(columns = {'Stock_Code_' : 'Stock_Code' , 'DateOnly_': 'Date'}, inplace = True)
    df_NewsScoreByStockNDate['Date'] = pd.to_datetime(df_NewsScoreByStockNDate['Date'])
    return df_NewsScoreByStockNDate


# Function to assign scores to the each news article based on FLAIR library ( pre-trained readymade model - https://pypi.org/project/flair/)
def AssignSentimentScores(dataFrameToAnalyze, columnNameInDataframeToAnalyze):
    dataFrameToAnalyze["Sentiment_Score"] = 0.0000
    for eachItemIndex in dataFrameToAnalyze.index :
        score_description = fl.data.Sentence(dataFrameToAnalyze[columnNameInDataframeToAnalyze][eachItemIndex])
        sentiment_model.predict(score_description)
        # Assigning score from -1 to +1 obtained ny multiplying probability with sentiment value ( POSITIVE (+1) or NEGATIVE(-1))
        scoreValueFromMinus1ToPlus1 = score_description.labels[0].score * (1 if score_description.labels[0].value == "POSITIVE" else -1)
        dataFrameToAnalyze["Sentiment_Score"][eachItemIndex] = scoreValueFromMinus1ToPlus1
    return dataFrameToAnalyze