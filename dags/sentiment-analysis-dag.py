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
    trump_tweets = pd.read_csv("/opt/airflow/data/hashtag_donaldtrump.csv", lineterminator='\n', parse_dates=True)
    jb_tweets = pd.read_csv("/opt/airflow/data/hashtag_joebiden.csv", lineterminator='\n', parse_dates=True)
    trump_tweets['presidential_candidate'] = 'trump'
    jb_tweets['presidential_candidate'] = 'biden'
    merged_tweets = pd.concat([trump_tweets, jb_tweets])
    merged_tweets.drop_duplicates(subset=['tweet_id', 'user_id'],inplace=True)
    merged_tweets['tweet'] = merged_tweets['tweet'].str.replace(r'@\S+|#\S+|https?://\S+|[^a-zA-Z\s]+', ' ', regex=True)
    merged_tweets['tweet'] = merged_tweets['tweet'].str.replace(r'\s+', ' ', regex=True).str.strip()
    merged_tweets.dropna(subset=['user_location', 'lat', 'long', 'city', 'country', 'state_code'], inplace=True)
    return

with DAG(
    dag_id="analyze_tweet_sentiment",
    start_date=pendulum.today("UTC"),
    schedule=None,
):
    clean_tweet_task = PythonOperator(
        task_id="clean_tweets",
        python_callable=_clean_tweets
    )
    
    