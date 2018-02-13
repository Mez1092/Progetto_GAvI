import argparse
import re
from xml.etree import ElementTree as ET
from xml.dom import minidom
import html.entities
import emot
from tqdm import tqdm
from googletrans import Translator
parser = argparse.ArgumentParser(description="Tokenize tweets text")
parser.add_argument("input_file", type=str,
					help="XML file input of tweets")
parser.add_argument("-o", "--output", dest="output_file", type=str,
					default='data/xml/texttw_tokenized.xml',
					help="XML file output of token tweets")
args = parser.parse_args()

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

	"""
	html_char = []
	for k in html5.keys():
		if ';' in k:
			html_char.append(k)
	html_pat = '|&'.join(html_char)

	html_chars = re.findall(html_pat, text)

	for h in html_chars:
		text = text.replace(h, '')

	return text"""

def find_emojis(text, item):
	""" Find emojis in text and create the respective xml element.
		Return the text without emojis.
	"""
	emojis = []
	for emoji in emot.emoji(text):
		emojis.append(emoji['value'])
		text = text.replace(emoji['value'], '')
	attr = ET.SubElement(item, 'EMOJIS')
	attr.text = ' '.join(emojis)

	return text

def find_screenname_rt(text, item):
	""" Find screen name and RT in text and crate the respective xml element.
		Return the text without screen name and RT.
	"""
	screenname_pat = "([RT]*\s?@[\w_]+[:]?)"
	screennames = re.findall(screenname_pat, text)

	attr = ET.SubElement(item, 'SCREENNAME_RT')
	attr.text = ' '.join(screennames).replace(':', '')

	for screenname in screennames:
		text = text.replace(screenname, '')

	return text

def find_hashtags(text, item, translate=False, src_language=None):
	""" Find hashtags in text and, if necessary, translate and create the respective xml element.
		Return text without hashtags.
	"""
	hashtags_pat = "(\#+[\w_]+[\w\'_\-]*[\w_]+)"
	hashtags = re.findall(hashtags_pat, text)
	hashtags.sort(key=len, reverse=True)		# for remove hashtags correctly from text
	for (i, hashtag) in enumerate(hashtags):	# remove '#'
		hashtags[i] = hashtag.replace('#', '')

	if translate:
		try:
			hashtags_tsl = Translator().translate(hashtags, src=src_language, dest='en')
		except ValueError:
			hashtags_tsl = Translator().translate(hashtags, dest='en')

		hashtags = []
		for h in hashtags_tsl:
			hashtags.append(h.text)

	attr = ET.SubElement(item, 'HASHTAGS')
	attr.text = ' '.join(hashtags)

	for tag in hashtags:
		text = text.replace(tag, '')

	return text

def find_urls(text, item):
	""" Find URLs in text and crate the respective xml element.
		Return the text without URLs.
	"""
	urls_pat = '(http[s]?\S*)'
	urls = re.findall(urls_pat, text)

	attr = ET.SubElement(item, 'URLS')
	attr.text = ' '.join(urls)

	for url in urls:
		text = text.replace(url, '')

	return text

def find_emoticons(text, item):
	""" Find emoticons in text and crate the respective xml element.
		Return the text without emoticons.
	"""
	emoticons_pat = "\s([<>]?[:;=B][\\-o\*\']?[\)\]\(\[[DbpP/\:\}\{@\|\\\\]+\s?|\s?[\)\]\(\[[dDbpP/\:\}\{@\|\\\\]+[\\-o\*\']?[:;=][<>]?)\s?"
	emoticons = re.findall(emoticons_pat, text)

	attr = ET.SubElement(item, 'EMOTICONS')
	attr.text = ' '.join(emoticons)

	for emoticon in emoticons:
		text = text.replace(emoticon, '')

	return text


if __name__ == '__main__':

	translator = Translator()
	tweets = ET.parse(args.input_file).getroot()
	root = ET.Element('TWEETS_TOKEN')

	# Tokenize and translate
	print("Analizing tweets...")
	for tweet in tqdm(tweets):

		tweet_id = tweet.attrib['ID']
		tweet_text = tweet.find('TEXTTW').text
		tweet_lang = tweet.find('LANG').text.replace(' ', '')

		# set ID
		item = ET.SubElement(root, 'TWEET')
		item.set('ID', tweet_id)

		# set language (this is necessary for successive step)
		attr = ET.SubElement(item, 'LANG')
		attr.text = tweet_lang

		tweet_text = find_emojis(tweet_text, item)
		tweet_text = html2unicode(tweet_text)
		tweet_text = find_urls(tweet_text, item)
		tweet_text = find_screenname_rt(tweet_text, item)
		tweet_text = find_hashtags(tweet_text, item, False, tweet_lang)
		tweet_text = find_emoticons(tweet_text, item)

		# Remaining text...
		pat = "([a-z][a-z'\-_]+[a-z]|[+\-]?\d+[,/.:-]\d+[+\-]?|[\w_]+)"
		tweet_text = ' '.join(re.findall(pat, tweet_text))
		re.sub('^\s+|(\s\s)+|\s$', '', tweet_text)	# remove useless space in text

		attr = ET.SubElement(item, 'PLAIN_TEXT')
		attr.text = tweet_text

	print("Write tokenized tweets on xml file...")
	xml = minidom.parseString(ET.tostring(root)).toprettyxml()
	with open(args.output_file, "w+") as file:
		file.write(xml)
