import re
import pandas as pd
from tqdm import tqdm
import argparse
import xml.etree.ElementTree as ET
from xml.dom import minidom
parser = argparse.ArgumentParser(description="Convert .txt file of tweets in a .xml file.")
# input argument
parser.add_argument("input_file", type=str,
                    help="Input text file of tweets")
# output argument
parser.add_argument("-o", "--output", dest="output_file", type=str,
                    default='data/xml/mostre.xml',
                    help="Output xml and csv file of tweets")
# do you want .csv?
parser.add_argument("--csv", dest="csv", action="store_true", help="If you want .csv also")
args = parser.parse_args()


if __name__ == '__main__':

    # Read all data
    with open(args.input_file, "r") as file:
        data = file.read()

    # Get list of single tweet
    start = 'TextTW : '
    data = data.split(start)[1:]

    # Get all features of each tweet
    label_pat = '\n([A-Z][a-zA-Z\_\-]+\ \:\ )'
    tweets = []
    print("Analyze the tweets...")
    for d in tqdm(data):
        tweet = {}
        labels = re.findall(label_pat, d)
        labels.insert(0, start)
        if 'Tweetid : ' in labels:
            if labels.index('Tweetid : ') != 1:
                labels.remove(labels[1])        # for catch all TextTW
        if 'Tweetid : ' not in labels:		    # tweet bad formatted
            continue
        for i in range(len(labels)):
            if i >= 0 and i < (len(labels)-1):
                split_word = labels[i+1]
                key = labels[i].replace(' : ', '').replace('-', '_').upper()
                content = re.sub('(\s)+$', '', d.split(split_word)[0].replace('\n', ' '))
                tweet[key] = content
                d = d.split(split_word)[1]
            elif i == (len(labels)-1):
                split_word = labels[i]
                key = labels[i].replace(' : ', '').replace('-', '_').upper()
                content = re.sub('(\s)+$', '', d.split(split_word)[0].replace('\n', ' '))
                tweet[key] = content
                d = ""

        tweets.append(tweet)

    # Write tweets to .xml
    print("Create xml structure...")
    root = ET.Element('TWEETS')
    for element in tqdm(tweets):
        item = ET.SubElement(root, 'TWEET')
        item.set('ID', element['TWEETID'])
        for k, v in element.items():
            if k == "TWEETID":
                continue
            attr = ET.SubElement(item, k)
            attr.text = v
    print("Write tweets on xml file...")
    xml = minidom.parseString(ET.tostring(root)).toprettyxml()
    with open(args.output_file, "w+") as file:
        file.write(xml)

    if args.csv:
        # Write tweets to .csv
        df = pd.DataFrame(tweets, dtype=None)
        df.set_index('TWEETID', inplace=True)
        print("Write tweets on csv file")
        df.to_csv(args.output_file.replace('xml', 'csv'))
