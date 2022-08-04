from pydoc import describe
import pandas as pd
import requests as httpRequest
from scrapy import Selector
import re

# investingdotcom_data = requests.get("https://in.investing.com/indices/s-p-cnx-nifty-components").content
# sel_investing = selector(text = investingdotcom_data)
tickertapedotcom_baseUrl = "https://tickertape.in/"
tickertape_stockurlSuffix = "/stocks/{0}/news?checklist=basic&type=news"
tickertapedotcom_stockList = httpRequest.get("https://www.tickertape.in/indices/nifty-50-index-.NSEI/constituents").content
sel_tickertape = Selector(text = tickertapedotcom_stockList)
stockSeedList_Links = sel_tickertape.xpath('//h5/a[starts-with(@href, "/stocks")]/@href').extract()
stockSeedList_Names = sel_tickertape.xpath('//h5/a[starts-with(@href, "/stocks")]/@title').extract()
StockListMetadata = pd.DataFrame({"Stock_FullName": [], "Stock_Code": [] , "Sector": [],"TickerTapeUrl" : [], "InvestingUrl" : []})
for (stockName, stockLink) in zip(stockSeedList_Names, stockSeedList_Links):
    StockListMetadata = StockListMetadata.append({'Stock_FullName' : str.split(stockName, "|")[0],
                                    'Stock_Code' : str.split(stockName, "|")[1],
                                    'Sector' : str.split(stockName, "|")[2], 'TickerTapeUrl' :  tickertapedotcom_baseUrl + tickertape_stockurlSuffix.replace('{0}', stockLink)},  ignore_index = True)