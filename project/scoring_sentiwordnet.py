from nltk.corpus import sentiwordnet as swn
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
import argparse
import numpy as np
import time
import pandas as pd
from tqdm import tqdm
from xml.etree import ElementTree as ET
parser = argparse.ArgumentParser()
parser.add_argument("input_file", type=str,
                    help="XML file input of tokenized tweets")
parser.add_argument('-o', '--output', type=str, dest='output_file',
                    default='data/csv/tweets_score.csv')
args = parser.parse_args()

def select_synset(words):
    """ Disambiguate words and return synset selected for each words.
    """
    synsets = []
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
    tweets_score = {}
    print("Calculate score for tweets...")
    for tweet in tqdm(tweets[:-200]):
        tweet_score = 0
        tweet_plain_text = tweet.find('PLAIN_TEXT').text
        tweet_id = tweet.attrib['ID']
        if tweet_plain_text is None:
            continue
        tweets_words = [t for t in tweet_plain_text.split() if t not in stopwords.words('english')]
        synsets = select_synset(tweets_words)

        for syn in synsets:
            pos_score = swn.senti_synset(syn.name()).pos_score()
            neg_score = swn.senti_synset(syn.name()).neg_score()

        tweet_score += neg_score
        tweet_score += pos_score

        tweets_score[tweet_id]=tweet_score
    print(tweets_score)
    df = pd.DataFrame.from_dict(tweets_score, orient='index')
    df.columns = ['SCORE']
    df.index.name = 'ID'
    df.to_csv(args.output_file)
