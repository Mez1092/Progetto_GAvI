>>> from xml.etree import ElementTree as TE
>>> from xml.etree import ElementTree as ET
>>> tweets = ET.parse('data/xml/tweets_tokenized.xml').getroot()
>>> tweets_en = tweets.findall('.//TWEET[LANG="en"]')
>>> for t in tweets_en:
...     if t.find('LANG').text != 'en':
...         print("Errore")
>>> root = ET.Element("TOKEN_TWEETS")
>>> for t in tweets_en:
...     item = ET.SubElement(root, 'TWEET')
...     item.set('ID', t.attrib['ID'])
...     for c in t:
...         attrib = ET.SubElement(item, c.tag)
...         attrib.text = t.find(c.tag).text
>>> from xml.dom import minidom
>>> xml = minidom.parseString(ET.tostring(root)).toprettyxml()
>>> with open('data/xml/tweets_tokenized_en.xml') as f:
...     f.write(xml)
Traceback (most recent call last):
  File "<stdin>", line 2, in <module>
io.UnsupportedOperation: not writable
not writable
>>> with open('data/xml/tweets_tokenized_en.xml', "w") as f:
...     f.write(xml)
>>> import pandas as pd
>>> tweets_df = pd.read_csv('data/csv/tweets_tokenized.csv')
>>> tweets_df = pd.read_csv('data/csv/tweets_tokenized.csv', index_col=0)
>>> tweets_df_en = tweets_df[tweets_df.LANG == 'en']
>>> tweets_df_en.shape
(31691, 6)
>>> tweets_df_en.to_csv('data/csv/tweets_tokenized_en.csv')