from nltk.sentiment.vader import SentimentIntensityAnalyzer as SA
from nltk.sentiment.vader import normalize
from nltk.corpus import stopwords
import argparse
import pandas as pd
import matplotlib
matplotlib.use('qt5agg')
from matplotlib import pyplot as plt
from tqdm import tqdm
from xml.etree import ElementTree as ET
parser = argparse.ArgumentParser()
parser.add_argument("input_file", type=str,
                    help="XML file input of tokenized tweets")
parser.add_argument('-o', '--output', type=str, dest='output_file',
                    default='data/csv/tweets_score_vader.csv')
args = parser.parse_args()


def calculate_scores(scores):
    pos = scores['pos']
    neg = scores['neg']
    neu = scores['neu']
    score = pos - neg
    if neu < 0.255:
        if pos > neg:
            score += neu
        elif pos < neg:
            score -= neu
    if neu > 0.85:
        if score > 0:
            score -= neu
        else:
            score += neu
    return score


if __name__ == '__main__':
    tweets = ET.parse(args.input_file).getroot()

    tweets_scores = {}

    sentiment_scores = SA().polarity_scores

    for tweet in tqdm(tweets):

        # intial score
        score = 0.0

        # count number of emoticons
        tweet_emoticons = tweet.find('EMOTICONS').text
        if tweet_emoticons:
            num_emoticons = len(tweet_emoticons.split())
        else:
            num_emoticons = 0

        # count number of emojis
        tweet_emojis = tweet.find('EMOJIS').text
        if tweet_emojis:
            num_emojis = len(tweet_emojis.split())
        else:
            num_emojis = 0

        # get plain text and ID of tweet
        tweet_id = tweet.attrib['ID']
        tweet_text = tweet.find('PLAIN_TEXT').text

        if tweet_text is None:
            continue
        else:
            words = [w for w in tweet_text.split() if w not in stopwords.words('english')]
            tweet_text = ' '.join(words)
            score = calculate_scores(sentiment_scores(tweet_text))

        # consider emoticons and emojis
        if score < 0:
            score -= (num_emojis**2)/4
            score -= (num_emoticons**2)/4
        else:
            score += (num_emojis**2)/4
            score += (num_emoticons**2)/4

        tweets_scores[tweet_id] = score

    for k, v in tweets_scores.items():
        n = normalize(v, alpha=1)
        tweets_scores[k] = n

    df = pd.DataFrame.from_dict(tweets_scores, orient='index')
    df.columns = ['SCORE']
    df.index.name = 'ID'
    df['SCORE'].plot('hist')

    ax = plt.gca()
    ax.set_title("Distribuzione punteggio dei tweet (vader)")
    ax.set_xlabel("Score")
    plt.show()

    df.to_csv(args.output_file)
