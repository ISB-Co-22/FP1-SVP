#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Library imports
import numpy as np
import pandas as pd
import requests
import os
import json
import requests
import csv
import tweepy as tweepy
import datetime
import time
from datetime import timedelta 
from datetime import date
import re
import emoji
from wordcloud import WordCloud, STOPWORDS
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
import nltk
import flair as fl
import torch
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
ps = PorterStemmer()
cleaned_tweets = []
nltk.download('vader_lexicon') #required for Sentiment Analysis
from textblob import TextBlob

import warnings
warnings.filterwarnings("ignore")


# In[2]:



def GetFilePath():
    filepath = '/Users/smaranika/Library/CloudStorage/OneDrive-Personal/Desktop/AMPBA/Term-2/Fundamental Project-1/Data/'
    return filepath

def GetStockInformation():
    filepath = GetFilePath()
    filename = filepath + 'StockName.xlsx'
    df = pd.read_excel (filename, sheet_name='trial')
    return df

def getTwitterAPI():
    consumer_key = "YcOQKS2GQ0Mf1CKRIW6GfnMqQ"
    consumer_secret = "45wgeIqKnO3eq3hmsDpRNvqSRKxAQ8i4P10eU2eeM1omNfySEq"
    access_key= "1548657834455597056-4zEaqWKKWURPqqPpMlSsr1jJQZF4EV"
    access_secret= "lIxCJcL1W3Jf4TIVth9SCyz7Mn1h3jQTF4d5qd8ZAT7lI"
    bearer_Token='AAAAAAAAAAAAAAAAAAAAAAu0ewEAAAAAnsItYb1cHn98OfQJkbDW8dRiG1c%3D5EUOyxvBRkRkiDgZuubPgHcjJ0EBYGzbWQkSJrJzOtazUAbJj9'
    
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)
    return api


# In[3]:



# function to perform data extraction
#Input Parameter: Keyword, date_since, tweetno (no of tweets to scrape to limit)
def dataextract(keyword, date_until, tweetno, company_name, result_type):
    status ="Error"
    stock_code = keyword.replace(" Stock", "")
    
    # Creating DataFrame to save tweets
    #Date	Company Name	Stock Code	Tweet	Source	Link	Engagement Metadata columns		
    TweetDataFrame = pd.DataFrame(columns=['date','company_name','stock_code','text','source'
                                           ,'link','location','retweetcount','likes', 'hashtags'])
    
    tweets = tweepy.Cursor(api.search_tweets, q=keyword, lang="en", until=date_until
                           , result_type=result_type, tweet_mode='extended').items(tweetno)
    list_tweets = [tweet for tweet in tweets]
    i = 1

    for tweet in list_tweets:

        date = tweet.created_at
        company_name = company_name
        stock_code = stock_code
        hashtags_ob = tweet.entities['hashtags']
        try:
            text = tweet.retweeted_status.full_text
        except AttributeError:
            text = tweet.full_text
        hashtext = list()
        for j in range(0, len(hashtags_ob)):
            hashtext.append(hashtags_ob[j]['text'])

        source = 'Twitter'
        link = ''
        location = tweet.user.location
        retweetcount = tweet.retweet_count
        likes = tweet.favorite_count
        hashtags = tweet.entities['hashtags']

        ith_tweet = [date,company_name,stock_code,text,source,link,
                            location,retweetcount,likes, hashtags]
        TweetDataFrame.loc[len(TweetDataFrame)] = ith_tweet

        i = i+1

            
    
    file_path = GetFilePath()
    fileDetails = file_path + 'TwitterSentiments.csv'
    
    TweetDataFrame.to_csv(fileDetails, mode='a', index=False, header=False)
    status = "Success"
    
    
    return status


# In[4]:


def GetTweetDataForPrediction(no_of_days,date_until):
    #Get Stock Information
    df = GetStockInformation()
    getTwitterAPI()
    
    date_1 = date_until
    date_1 = datetime.datetime.strptime(date_until, "%Y-%m-%d")
    result_type='mixed'
    tweetno = 50
    while(no_of_days>0):
    
        date_1 =date_1 + datetime.timedelta(days=1)
        date_until=date_1
    
        no_of_days = no_of_days-1
    
        for index, row in df.iterrows():
    
            if((index+1)%5 == 0):
                print('Resting: Scrapping done for stocks:',index)
                time.sleep(60*5)
                print('Wait Over',index+1)
            Stock_Code = row["Stock_Code"]
            companyname = row["Stock_FullName"]
            keyword = Stock_Code + ' Stock'
            end = dataextract(keyword, date_until, tweetno, companyname,result_type) 
                
        print("Extracting for next day")
    return 1  



def GetTweetDailyDataForPred():

    #Get Stock Information & API
    df = GetStockInformation()
    api=getTwitterAPI()

    
    start_time = datetime.datetime.now()
    print('start time:',start_time)
    
    today = date.today()+ timedelta(days=1) 
    date_until = today.strftime("%Y-%m-%d")
    tweetno = 50
    result_type='recent'

    date_until = '2022-08-09'

    for index, row in df.iterrows():

        if((index+1)%5 == 0):
            print('Resting: Scrapping done for stocks:',index+1)
            time.sleep(60*5)
            print('Wait Over',index+1)
        Stock_Code = row["Stock_Code"]
        companyname = row["Stock_FullName"]
        keyword = Stock_Code + ' Stock'
        end = dataextract(keyword, date_until, tweetno, companyname,result_type)  


    if(end == 'Success'):
        print('Scraping has completed!')
        print(date_until)
    else:
        print("Error")
    end_time = datetime.datetime.now()
    print('end time:',end_time)    

def MaintainMasterSheet():

    today = date.today()

    filename1 = 'TwitterSentimentsMasterSheet.csv'
    filename2 = 'TwitterSentiments.csv'

    filepath = GetFilePath()
    
    df1 = pd.read_csv(filepath+filename1)
    #df1.columns= ['date','company_name','stock_code','text','source','link','location','retweetcount','likes', 'hashtags']     


    df2 = pd.read_csv(filepath+filename2)
    #df2.columns= ['date','company_name','stock_code','text','source','link','location','retweetcount','likes', 'hashtags']     


    df = pd.concat([df1, df2])
    df3 = df.drop_duplicates()
    ConsolidateFileName='TwitterSentiments'+'_'+ today.strftime("%B%d") + '.csv'

    df3.to_csv(filepath+ConsolidateFileName, index=False)
    
    df3.to_csv(filepath+'TwitterSentimentsMasterSheet_1'+ '.csv', index=False)
    
    return 1


def AssignTweetSentimentScores(dataFrameToAnalyze, columnNameInDataframeToAnalyze):
    sentiment_model = fl.models.TextClassifier.load('en-sentiment')
    dataFrameToAnalyze["Sentiment_Score"] = 0.0000
    dataFrameToAnalyze["Sentiment_Val"] = ""
    dataFrameToAnalyze["Sentiment_Prob"] = 0.0000
    for eachItemIndex in dataFrameToAnalyze.index :
        score_description = fl.data.Sentence(dataFrameToAnalyze[columnNameInDataframeToAnalyze][eachItemIndex])
        sentiment_model.predict(score_description)
        dataFrameToAnalyze["Sentiment_Val"][eachItemIndex] = score_description.labels[0].value
        dataFrameToAnalyze["Sentiment_Prob"][eachItemIndex] = score_description.labels[0].score
        # Assigning score from -1 to +1 obtained ny multiplying probability with sentiment value ( POSITIVE (+1) or NEGATIVE(-1))
        scoreValueFromMinus1ToPlus1 = score_description.labels[0].score * (1 if score_description.labels[0].value == "POSITIVE" else -1)
        dataFrameToAnalyze["Sentiment_Score"][eachItemIndex] = scoreValueFromMinus1ToPlus1
    return dataFrameToAnalyze


# In[38]:


# Create a function to clean the tweets
def cleanText(text):
    text = re.sub('@[A-Za-z0–9]+', '', text) 
    text = re.sub('#', '', text) 
    text = re.sub('RT[\s]+', '', text) 
    text = re.sub('https?:\/\/\S+', '', text) 
    return text
    
    

def ProcessTweets():
    
    filepath = GetFilePath()
    inputfilename = 'TwitterSentimentsMasterSheet.csv'

    df1 = pd.read_csv(filepath+inputfilename)
    df1.columns= ['datetime','company_name','stock_code','text','source','link','location','retweetcount','likes', 'hashtags']     
    df1['text']=df1['text'].apply(str)
    #df['cleaned_tweets'] = ''
    for i, row in df1.iterrows():
        text = df1['text'][i]
        tweets = cleanText(text)
        tweets = tweets.lower()
        #tweets = tweets.split()
        #tweets = [ps.stem(word) for word in tweets if not word in set(stopwords.words('english'))]
        #tweets = ' '.join(tweets)
        cleaned_tweets.append(tweets)
        

    df1['cleaned_tweets'] = pd.Series(cleaned_tweets)
    
    # Add a new column to keep Date part only
    df1["Date"] = pd.to_datetime(df1["datetime"]).dt.date
    df1 = df1.drop(['datetime','company_name','text'
                        ,'source','link','location','retweetcount','likes', 'hashtags'] , axis = 1)
    
    Sentiment_Score = []
    Sentiment_Value = []
    for i, row in df1.iterrows():
        blob = TextBlob(df1["cleaned_tweets"][i])
        Sentiment_Score.append(blob.sentiment.polarity)
        Sentiment_Value.append(blob.sentiment.subjectivity)
    df1['Sentiment_Score'] = pd.Series(Sentiment_Score)
    #df1['Sentiment_Value'] = pd.Series(Sentiment_Value)  

    df1 = df1[['Date', 'stock_code', 'Sentiment_Score']]
    df1.to_csv(filepath+'TwitterSentimentsAlldates'+ '.csv', index=False)
    # Aggregating Sentiment scores for every combination of StockCode and Date
    df1 = df1.groupby(['stock_code', 'Date']).agg({'Sentiment_Score': ['mean']})

    
    return df1


# In[39]:


#For Daily Prediction
#GetTweetDailyDataForPred()
#MaintainMasterSheet()

df1= ProcessTweets()

    
df1.head()


# In[ ]:




