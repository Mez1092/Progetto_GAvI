from nltk.sentiment.vader import SentimentIntensityAnalyzer as SA
import argparse
import numpy as np
import time
import pandas as pd
from matplotlib import pyplot as plt
from tqdm import tqdm
from xml.etree import ElementTree as ET
parser = argparse.ArgumentParser()
parser.add_argument("input_file", type=str,
                    help="XML file input of tokenized tweets")
parser.add_argument('-o', '--output', type=str, dest='output_file',
                    default='data/csv/tweets_score.csv')
args = parser.parse_args()

def calculate_score(sentiment_scores):
    pos = sentiment_scores['pos']
    neg = sentiment_scores['neg']
    neu = sentiment_scores['neu']
    score = pos - neg
    if pos > (neu+0.35) or neg > (neu+0.35):
        if pos > neg:
            score += neu
        elif neg > pos:
            score -= neu
    if neu > 0.75:
        score =- 0.15*score
    return score

if __name__ == '__main__':
    tweets = ET.parse(args.input_file).getroot()
    tweets_score = {}
    for tweet in tqdm(tweets):
        tweet_text = tweet.find('PLAIN_TEXT').text
        tweet_id = tweet.attrib['ID']
        if tweet_text == None:
            score = 0
        else:
            score = calculate_score(SA().polarity_scores(tweet_text))
        tweets_score[tweet_id] = score

    df = pd.DataFrame.from_dict(tweets_score, orient='index')
    df.columns = ['SCORE']
    df.index.name = 'ID'
    df['SCORE'].plot('hist')
    plt.show()
    df.to_csv(args.output_file)
