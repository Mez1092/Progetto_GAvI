from xml.etree import ElementTree as ET
import argparse
from googletrans import Translator
import re
import html.entities
from nltk.stem.wordnet import WordNetLemmatizer
from tqdm import tqdm
from xml.dom.minidom import parseString
from joblib import Parallel, delayed

parser = argparse.ArgumentParser()
parser.add_argument("input_file", type=argparse.FileType("r"), help="XML file containing tokenized tweets")
parser.add_argument("output_file", type=argparse.FileType("w+"), nargs='?', default='data/xml/tweets_translated.xml',
                    help="XML file to save translated tweets (data/xml/tweets_translated.xml by default)")
args = parser.parse_args()


def html2unicode(text):
    """	Convert HTML entities in unicode char.
    """
    html_entity_digit_re = re.compile(r"&#\d+;")
    html_entity_alpha_re = re.compile(r"&\w+;")
    amp = "&amp;"

    # digit
    ents = set(html_entity_digit_re.findall(text))
    if len(ents) > 0:
        for ent in ents:
            entnum = ent[2:-1]
            entnum = int(entnum)
            text = text.replace(ent, chr(entnum))

    # alpha
    ents = set(html_entity_alpha_re.findall(text))
    ents = filter((lambda x: x != amp), ents)
    for ent in ents:
        entname = ent[1:-1]
        text = text.replace(ent, chr(html.entities.name2codepoint[entname]))

    text = text.replace(amp, " and ")

    return text


def Translate(tweet):
    try:
        for tweet in tqdm(tweets):
            # new xml file
            item = ET.SubElement(root, 'TWEET')
            item.set('ID', tweet.attrib['ID'])
            for t in tweet:
                attrib = ET.SubElement(item, t.tag)
                attrib.text = tweet.find(t.tag).text

            tweet_lang = tweet.find('LANG').text
            tweet_text = tweet.find('PLAIN_TEXT').text

            # default no translate
            if tweet_text is not None:
                translated_text = tweet_text
            else: translated_text = ""

            # translate...
            if tweet_text is not None and tweet_lang != 'en' and tweet_lang != 'und':
                try:
                    translated_text = Translator().translate(tweet_text, src=tweet_lang, dest='en').text
                except ValueError:
                    pass
                translated_text = html2unicode(translated_text)



            attrib = ET.SubElement(item, 'Translated_text')
            attrib.text = translated_text

            # stemming...
            stemmer = WordNetLemmatizer()
            stemmed_text = [stemmer.lemmatize(word) for word in translated_text.split()]

            attrib = ET.SubElement(item, 'Stemmed_text')
            attrib.text = ' '.join(stemmed_text)
    except:
        print("Translation not complete....")
        xml = parseString(ET.tostring(root)).toprettyxml()
        args.output_file.write(xml)



if __name__ == '__main__':


    # tweets = ET.parse(args.input_file.name).getroot()
    tree = ET.parse(args.input_file.name)
    tweets = tree.getroot()

    root = ET.Element('TRANSLATED_TOKENIZED_TWEETS')

    print("Analizing and translate tweets...")

    results = Parallel(n_jobs=8)(delayed(Translate)(tweet) for tweet in tweets)

    tree.write(args.input_file.name)




