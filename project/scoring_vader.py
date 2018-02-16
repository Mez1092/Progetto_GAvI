from nltk.sentiment.vader import SentimentIntensityAnalyzer as SA
import argparse
import pandas as pd
from tqdm import tqdm
from xml.etree import ElementTree as ET
parser = argparse.ArgumentParser(description="Compute score of each tweet using vader library")
parser.add_argument("input_file", type=argparse.FileType("r"), help="XML file input of tokenized tweets")
parser.add_argument("output_file", type=argparse.FileType("w+"), nargs='?', default='data/csv/tweets_score_vader.csv',
                    help="CSV output file of tweets score")
args = parser.parse_args()


if __name__ == '__main__':
    tweets = ET.parse(args.input_file.name).getroot()

    tweets_scores = []

    sentiment_scores = SA().polarity_scores

    for tweet in tqdm(tweets):

        # intial score
        tweet_score = 0.0

        # get plain text and ID of tweet
        tweet_id = tweet.attrib['ID']
        tweet_text = tweet.find('PLAIN_TEXT').text

        tweet_sentiment_analysis = dict()
        tweet_sentiment_analysis['id'] = tweet_id

        # count number of emojis
        tweet_emojis = tweet.find('EMOJIS').text
        if tweet_emojis:
            num_emojis = len(tweet_emojis.split())
        else:
            num_emojis = 0

        if tweet_text is not None:
            pos = sentiment_scores(tweet_text)['pos']
            neg = sentiment_scores(tweet_text)['neg']
            tweet_score = pos - neg

        # consider emojis and emoticons
        if tweet_score < 0:
            tweet_score -= num_emojis*0.2
        elif tweet_score > 0:
            tweet_score += num_emojis*0.2
        else:
            if tweet_emojis:
                tweet_score += num_emojis*0.2

        tweet_sentiment_analysis['score'] = tweet_score
        if tweet_score > 0:
            tweet_sentiment_analysis['polarity'] = "Positive"
        elif tweet_score < 0:
            tweet_sentiment_analysis['polarity'] = "Negative"
        else:
            tweet_sentiment_analysis['polarity'] = "Neutral"

        tweets_scores.append(tweet_sentiment_analysis)

    df = pd.DataFrame(tweets_scores)
    df.set_index('id', inplace=True)

    df.to_csv(args.output_file.name)
