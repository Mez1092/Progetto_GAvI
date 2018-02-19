from xml.etree import ElementTree as ET
import argparse
from googletrans import Translator
from tqdm import tqdm
from xml.dom.minidom import parseString
parser = argparse.ArgumentParser()
parser.add_argument("input", type=str, help="Input text file of tweets tokenized")
parser.add_argument("-o", "--output", dest="output_file", type=str,
                    default='data/processed/tweets_translated.xml',
                    help="Output xml file of translated tweets")
args = parser.parse_args()


if __name__ == '__main__':
    tweets = ET.parse(args.input).getroot()

    print("Analizing and translate tweets...")
    for tweet in tqdm(tweets):
        tweet_lang = tweet.find('LANG').text.replace(' ','')
        tweet_text = tweet.find('PLAIN_TEXT').text

        translated_text = None
        if tweet_text is not None and tweet_lang != 'en':
            try:
                translated_text = Translator().translate(tweet_text, src=tweet_lang, dest='en')
            except ValueError:
                translated_text = Translator().translate(tweet_text, dest='en')

        attr = ET.SubElement(tweet, 'TRANSLATED_TEXT')

        if translated_text is not None:
            attr.text = translated_text.text
    
    xml = parseString(ET.tostring(tweets)).toprettyxml()

    with open(args.output_file, "w+") as f:
        f.write(xml)