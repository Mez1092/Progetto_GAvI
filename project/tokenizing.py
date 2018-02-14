import re
import emot
import pandas as pd
from xml.etree import ElementTree as ET
from xml.dom import minidom
from nltk.sentiment.util import HAPPY, SAD
import argparse
from tqdm import tqdm
parser = argparse.ArgumentParser(description="Tokenize tweets text")
parser.add_argument("input_file", type=str,
					help="XML file input of tweets")
parser.add_argument("-o", "--output", dest="output_file", type=str,
					default='data/xml/tweets_tokenized.xml',
					help="XML file output of token tweets")
parser.add_argument("--csv", dest="csv", action="store_true", help="If you want csv also")
args = parser.parse_args()

emoticon_string = r"""
    (?:
      [<>]?
      [:;=8]                     # eyes
      [\-o\*\']?                 # optional nose
      [\)\]\(\[dDpP/\:\}\{@\|\\] # mouth
      |
      [\)\]\(\[dDpP/\:\}\{@\|\\] # mouth
      [\-o\*\']?                 # optional nose
      [:;=8]                     # eyes
      [<>]?
    )"""

regex_strings = (
    # Emoticons:
    emoticon_string
    ,
    # HTML tags:
    r"""(?:<[^>]+>)"""
    ,
    # Retweet
    r"""RT"""
    ,
    # URLs:
    r"""(?:http[s]?[\w\W]+)"""
    ,
    # Twitter username:
	r"""(?:@[\w_]+:?)"""
    ,
    # Twitter hashtags:
    r"""(?:\#+[\w_]+[\w\'_\-]*[\w_]+)"""
    ,
    # Remaining word types:
    r"""
    (?:[a-z][a-z'\-_]+[a-z])       # Words with apostrophes or dashes.
    |
    (?:[+\-]?\d+[,/.:-]\d+[+\-]?)  # Numbers, including fractions, decimals.
    |
    (?:[\w_]+)                     # Words without apostrophes or dashes.
    |
    (?:\.(?:\s*\.){1,})            # Ellipsis dots.
    |
    (?:\S)                         # Everything else that isn't whitespace.
    """
    )

word_re = re.compile(r"""(%s)""" % "|".join(regex_strings), re.VERBOSE | re.I | re.UNICODE)

def html2unicode(text):
	"""	Convert HTML entities in unicode char.
	"""
	html_entity_digit_re = "&#\d+;"
	html_entity_alpha_re = re.compile(r"&\w+;")
	amp = "&amp;"

	# digit
	ents = set(re.findall(html_entity_digit_re, text))
	if len(ents) > 0:
		for ent in ents:
			entnum = ent[2:-1]
			try:
				entnum = int(entnum)
				text = text.replace(ent, char(entnum))
			except:
				pass

	# alpha
	ents = set(re.findall(html_entity_alpha_re, text))
	ents = filter((lambda x: x != amp), ents)
	for ent in ents:
		entname = ent[1:-1]
		try:
			text = text.replace(ent, char(html.entities.name2codepoint[entname]))
		except:
			pass
	text = text.replace(amp, " and ")

	return text

def find_emojis(text):
	""" Find and remove emojis in text.
		Return emojis founded and text without emojis.
	"""
	emojis = []
	for emoji in emot.emoji(text):
		emojis.append(emoji['value'])
		text = text.replace(emoji['value'], '')

	return text, emojis

def split_hashtags(hashtag):
	""" Split camel case hashtag
		Return splitted hashtag
	"""
	matches = re.findall('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', hashtag)
	return matches

if __name__ == '__main__':
	tweets = ET.parse(args.input_file).getroot()

	tweets_text = []
	print("Tokenizing tweets...")
	for tweet in tqdm(tweets):

		tweet_text = tweet.find('TEXTTW').text
		tweet_id = tweet.attrib['ID']
		tweet_lang = tweet.find('LANG').text

		hashtags = []
		emoticons = []
		emojis = []
		plain_text = []

		text_token = dict()
		text_token['ID'] = tweet_id
		text_token['ORIGINAL_TEXT'] = tweet_text
		text_token['LANG'] = tweet_lang

		tweet_text = html2unicode(tweet_text)

		tweet_text, emojis = find_emojis(tweet_text)

		tokens = word_re.findall(tweet_text)
		for token in tokens:
			if token.startswith('#'):									# is hashtag
				hashtags.append(token.replace('#', '').lower())
				hasthtag_text = split_hashtags(token.replace('#', ''))	# split camel case
				for hashtag in hasthtag_text:
					plain_text.append(hashtag.lower())
			elif token.startswith('@'):									# is screen name
				pass
			elif token.startswith('http'): 								# is a link
				pass
			elif token.startswith('RT'):								# is re-tweet
				pass
			elif (token in HAPPY) or (token in SAD):					# is emoticon
				emoticons.append(token)
			else:
				text = re.sub('[\_\-]', ' ', token).lower()				# adjust plain text
				plain_text.append(text)									# is plain text

		text_token['HASHTAGS'] = ' '.join(hashtags)
		text_token['EMOTICONS'] = ' '.join(emoticons)
		text_token['EMOJIS'] = ' '.join(emojis)
		text_token['PLAIN_TEXT'] = ' '.join(plain_text)
		tweets_text.append(text_token)

	print("Write token in xml file...")
	root = ET.Element('TOKEN_TWEETS')
	for t in tweets_text:
		item = ET.SubElement(root, 'TWEET')
		item.set('ID', t['ID'])
		for k, v in t.items():
			if k == 'ID':
				continue
			attrib = ET.SubElement(item, k)
			attrib.text = v
	xml = minidom.parseString(ET.tostring(root)).toprettyxml()
	with open(args.output_file, "w+") as file:
		file.write(xml)

	if args.csv:
		print("Write token in csv file...")
		df = pd.DataFrame(tweets_text)
		df.set_index('ID', inplace=True)
		df.to_csv(args.output_file.replace('xml', 'csv'))
