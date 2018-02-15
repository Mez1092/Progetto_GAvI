from xml.etree import ElementTree as ET
from xml.dom import minidom
import pandas as pd
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("input")
parser.add_argument("output")
args = parser.parse_args()

tweets = ET.parse(args.input).getroot()
tweets_en = tweets.findall('.//TWEET[LANG="en"]')
for t in tweets_en:
    if t.find('LANG').text != 'en':
        print("Errore")
root = ET.Element("TOKEN_TWEETS")
for t in tweets_en:
    item = ET.SubElement(root, 'TWEET')
    item.set('ID', t.attrib['ID'])
    for c in t:
        attrib = ET.SubElement(item, c.tag)
        attrib.text = t.find(c.tag).text

xml = minidom.parseString(ET.tostring(root)).toprettyxml()

with open(args.output, "w") as f:
    f.write(xml)

# tweets_df = pd.read_csv('data/csv/tweets_tokenized.csv', index_col=0)
# tweets_df_en = tweets_df[tweets_df.LANG == 'en']
# tweets_df_en.to_csv('data/csv/tweets_tokenized_en.csv')
