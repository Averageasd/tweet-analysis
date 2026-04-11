import pendulum
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG

import pandas as pd 
import pycld2 as cld2
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk
import matplotlib.pyplot as plt
import plotly.express as px
nltk.download("vader_lexicon")
import seaborn as sns
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('punkt_tab')      
nltk.download('wordnet')    
nltk.download('omw-1.4') 
nltk.download('averaged_perceptron_tagger_eng') 
sid_obj = SentimentIntensityAnalyzer()
lemmatizer = WordNetLemmatizer()

def _clean_tweets():
    trump_tweets = pd.read_csv(
        "/opt/airflow/data/hashtag_donaldtrump.csv", 
        lineterminator='\n', 
        parse_dates=True
    )
    jb_tweets = pd.read_csv(
        "/opt/airflow/data/hashtag_joebiden.csv", 
        lineterminator='\n', 
        parse_dates=True
    )
    
    trump_tweets['presidential_candidate'] = 'trump'
    jb_tweets['presidential_candidate'] = 'biden'
    merged_tweets = pd.concat([trump_tweets, jb_tweets])
    merged_tweets.drop_duplicates(subset=['tweet_id', 'user_id'],inplace=True)
    merged_tweets['tweet'] = merged_tweets['tweet'].str.replace(r'@\S+|#\S+|https?://\S+|[^a-zA-Z\s]+', ' ', regex=True)
    merged_tweets['tweet'] = merged_tweets['tweet'].str.replace(r'\s+', ' ', regex=True).str.strip()
    merged_tweets.dropna(
        subset=[
            'user_location', 
            'lat', 
            'long', 
            'city', 
            'country', 
            'tweet',
            'state_code'
        ], 
        inplace=True
        )
    merged_tweets.drop(axis=1, columns=[
    'retweet_count', 
    'user_name', 
    'user_screen_name', 
    'user_description', 
    'source', 
    'user_id',
    'user_location',
    'user_join_date', 
    'user_followers_count',
    'collected_at',
    'state_code'
    ], inplace=True)
    
    merged_tweets = merged_tweets.reset_index(drop=True)
    merged_tweets['created_at'] = pd.to_datetime(
        merged_tweets['created_at'], 
        format='mixed'
    )
    merged_tweets['created_at'] = (
        merged_tweets['created_at'].dt.date
    )
    
    target_file = "/opt/airflow/data/stage_tweets.csv"
    merged_tweets.to_csv(target_file)

def _lemmatize_and_sentiment(sentence):
    sentence = str(sentence)
    tokens = word_tokenize(sentence.lower())
    lemmatized_text = ' '.join([lemmatizer.lemmatize(word) for word in tokens])
    sentiment_dict = sid_obj.polarity_scores(lemmatized_text)
    if sentiment_dict['compound'] >= 0.05:
        return "pos"
    elif sentiment_dict['compound'] <= -0.05:
        return "neg"
    else:
        return "neu"

def _detect_lang(sentence):
    sentence = str(sentence)
    isReliable, textBytesFound, details = cld2.detect(
        sentence
    )
    return details[0][1]

def _calculate_sentiment():
    staged_tweets = pd.read_csv(
        "/opt/airflow/data/stage_tweets.csv"
    )
    staged_tweets['lang'] = staged_tweets['tweet'].apply(_detect_lang)
    staged_tweets = staged_tweets.loc[(staged_tweets['country'] == 'United States of America') & (staged_tweets['lang'] == 'en')]
    staged_tweets['sentiment'] = staged_tweets['tweet'].apply(_lemmatize_and_sentiment)
    staged_tweets.reset_index(drop=True, inplace=True)
    staged_tweets.to_csv("/opt/airflow/data/cleansed_tweets.csv")


with DAG(
    dag_id="analyze_tweet_sentiment",
    start_date=pendulum.today("UTC"),
    schedule=None,
):
    clean_tweet_task = PythonOperator(
        task_id="clean_tweets",
        python_callable=_clean_tweets
    )
    
    apply_sentiment_task = PythonOperator(
        task_id="apply_sentiment",
        python_callable=_calculate_sentiment
    )
    
    clean_tweet_task >> apply_sentiment_task
    
    