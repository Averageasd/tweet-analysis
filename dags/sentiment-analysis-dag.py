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

