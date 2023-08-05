import json, os, re
DIR_NAME = os.path.dirname(os.path.abspath(__file__))
STOPWORD_JSON = json.load(open(os.path.join(DIR_NAME, 'stopwords.json'), 'r'))

def getStopList():
	return STOPWORD_JSON