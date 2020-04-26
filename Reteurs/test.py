from nltk import FreqDist
from nltk.corpus import reuters, stopwords
import csv
import operator
from nltk import collections, ngrams
import config
from linguistic_processor import linguistic_module
import xml.etree.ElementTree as ET
from tqdm import tqdm
global RELEVANCE_DICT_REUTERS
from Reteurs.relevance_feeback import RELEVANCE_DICT_UOTTAWA, RELEVANCE_DICT_REUTERS
import Reteurs.relevance_feeback as rf


import config

print(rf.get_relevance('potatoe', 55, config.UOTTAWA))

rf.update_relevance('potatoe', 55, config.UOTTAWA)
print(rf.RELEVANCE_DICT_UOTTAWA)
print(rf.get_relevance('potatoe', 55, config.UOTTAWA))

rf.update_relevance('potatoe', 55, config.UOTTAWA)
print(rf.RELEVANCE_DICT_UOTTAWA)
print(rf.get_relevance('potatoe', 55, config.UOTTAWA))

rf.update_relevance('potatoe', 65, config.UOTTAWA)
print(rf.RELEVANCE_DICT_UOTTAWA)
print(rf.get_relevance('potatoe', 55, config.UOTTAWA))