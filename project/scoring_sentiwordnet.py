from nltk.corpus import sentiwordnet as swn
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.sentiment.util import mark_negation
from nltk.sentiment.util import HAPPY as happy_emoticons
from nltk.sentiment.util import SAD as sad_emotions
from nltk.stem.wordnet import WordNetLemmatizer
import argparse
import pandas as pd
from tqdm import tqdm
from xml.etree import ElementTree as ET
parser = argparse.ArgumentParser(description="Compute score of each tweet using nltk 'sentiwordnet' library")
parser.add_argument("input_file", type=argparse.FileType("r"), help="XML file input of tokenized tweets")
parser.add_argument("output_file", type=argparse.FileType("w+"), nargs='?', default='data/csv/tweets_score_swn.csv')
parser.add_argument('--disambiguate', action='store_true')
args = parser.parse_args()


def select_synset(words):
    """ Return a specific synset for each words.
    """
    synsets = {}

    # no disambiguate, select first
    if not args.disambiguate:
        for word in words:
            clean_word = word.replace('_NEG', '')
            if wn.synsets(clean_word):
                synsets[word] = wn.synsets(clean_word)[0]
        return synsets

    # disambiguate terms
    for word in words:
        clean_word = word.replace('_NEG', '')   # clean if this word is after a negation mark
        word_sense = None
        word_score = 0.0
        for word_syn in wn.synsets(clean_word, wn.NOUN):
            score_syn = 0.0
            for word2 in words:
                if word2 == word:
                    continue
                clean_word2 = word2.replace('_NEG', '')     # clean if this word is after a negation mark
                best_score = 0.0
                for word2_syn in wn.synsets(clean_word2, wn.NOUN):
                    temp_score = word_syn.wup_similarity(word2_syn)
                    if temp_score > best_score:
                        best_score = temp_score
                score_syn += best_score
            if score_syn > word_score:
                word_score = score_syn
                word_sense = word_syn
        if word_sense is not None:
            synsets[word] = word_sense
        elif wn.synsets(clean_word):
            synsets[word] = wn.synsets(clean_word)[0]
    return synsets


if __name__ == '__main__':

    tweets = ET.parse(args.input_file.name).getroot()

    tweets_scores = []

    print("Calculate score for tweets...")
    for tweet in tqdm(tweets):

        # initial score for tweet
        tweet_score = 0.0

        # get plain text and ID of the tweet
        tweet_plain_text = tweet.find('PLAIN_TEXT').text
        tweet_id = tweet.attrib['ID']

        tweet_sentiment_analysis = dict()
        tweet_sentiment_analysis['id'] = tweet_id

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

        if tweet_plain_text is not None:
            # stemming
            stemmer = WordNetLemmatizer()
            tweets_words = [stemmer.lemmatize(word) for word in tweet_plain_text.split()]

            # mark negation
            tweets_words = mark_negation(tweets_words)

            # remove stopwords
            tweets_words = [t for t in tweet_plain_text.split() if t not in stopwords.words('english')]

            ################################################################################################
            ## !! NOTA: Stemming, Mark negation e rimozione stopwords meglio metterle nella traduzione !! ##
            ################################################################################################

            # select synset of each term
            synsets = select_synset(tweets_words)

            # calculate score
            for word, sense in synsets.items():
                pos_score = swn.senti_synset(sense.name()).pos_score()
                neg_score = swn.senti_synset(sense.name()).neg_score()
                if '_NEG' in word:
                    temp = pos_score
                    pos_score = neg_score
                    neg_score = temp
                tweet_score += (pos_score - neg_score)

        # consider emojis and emoticons
        if tweet_score < 0:
            tweet_score -= num_emojis*0.2
            tweet_score -= num_emoticons*0.2
        elif tweet_score > 0:
            tweet_score += num_emojis*0.2
            tweet_score += num_emoticons*0.2
        else:
            if tweet_emoticons:
                for emoticons in tweet_emoticons.split():
                    if emoticons in happy_emoticons:
                        tweet_score += 0.2
                    elif emoticons in sad_emotions:
                        tweet_score -= 0.2

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
