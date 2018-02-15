from nltk.corpus import sentiwordnet as swn
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
import argparse
import matplotlib
matplotlib.use('qt5agg')
from matplotlib import pyplot as plt
import pandas as pd
from nltk.sentiment.vader import normalize
from tqdm import tqdm
from xml.etree import ElementTree as ET
parser = argparse.ArgumentParser()
parser.add_argument("input_file", type=str,
                    help="XML file input of tokenized tweets")
parser.add_argument('-o', '--output', type=str, dest='output_file',
                    default='data/csv/tweets_score_swn.csv')
parser.add_argument('--disambiguate', action='store_true')
args = parser.parse_args()


def select_synset(words):
    """ Disambiguate words and return synset selected for each words.
    """
    synsets = []
    if not args.disambiguate:
        for w in words:
            if wn.synsets(w):
                synsets.append(wn.synsets(w)[0])
        return synsets

    # disambiguate terms
    for word in words:
        word_sense = None
        word_score = 0.0
        for word_syn in wn.synsets(word, wn.NOUN):
            score_syn = 0.0
            for word2 in words:
                if word2 == word:
                    continue
                best_score = 0.0
                for word2_syn in wn.synsets(word2, wn.NOUN):
                    temp_score = word_syn.wup_similarity(word2_syn)
                    if temp_score > best_score:
                        best_score = temp_score
                score_syn += best_score
            if score_syn > word_score:
                word_score = score_syn
                word_sense = word_syn
        if word_sense is not None:
            synsets.append(word_sense)
    return synsets


if __name__ == '__main__':

    tweets = ET.parse(args.input_file).getroot()
    tweets_scores = {}

    print("Calculate score for tweets...")
    for tweet in tqdm(tweets):
        # initial score for tweet
        tweet_score = 0.0

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

        # get plain text and ID of the tweet
        tweet_plain_text = tweet.find('PLAIN_TEXT').text
        tweet_id = tweet.attrib['ID']

        if tweet_plain_text is None:
            tweets_scores[tweet_id] = tweet_score
            continue

        tweets_words = [t for t in tweet_plain_text.split() if t not in stopwords.words('english')]
        synsets = select_synset(tweets_words)
        num_words = len(synsets)

        if num_words == 0:
            tweets_scores[tweet_id] = tweet_score
            continue

        for syn in synsets:
            tweet_score += swn.senti_synset(syn.name()).pos_score()
            tweet_score -= swn.senti_synset(syn.name()).neg_score()

        # consider emojis and emoticons
        if tweet_score < 0:
            tweet_score -= (num_emojis**2)/4
            tweet_score -= (num_emoticons**2)/4
        else:
            tweet_score += (num_emojis**2)/4
            tweet_score += (num_emoticons**2)/4

        tweets_scores[tweet_id] = tweet_score

    # normalize [-1, 1]
    for k, v in tweets_scores.items():
        n = normalize(v, alpha=1)
        tweets_scores[k] = n

    df = pd.DataFrame.from_dict(tweets_scores, orient='index')
    df.columns = ['SCORE']
    df.index.name = 'ID'
    df['SCORE'].plot('hist')

    ax = plt.gca()
    ax.set_xlabel("Score")
    title = "Distribuzione punteggio dei tweet (sentiwordnet "
    if args.disambiguate:
        title = title + " con disambiguazione)"
    else:
        title = title + ")"
    ax.set_title(title)
    plt.show()

    df.to_csv(args.output_file)
