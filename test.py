from nltk import FreqDist
import csv
import config
from linguistic_processor import linguistic_module
from tqdm import tqdm
global RELEVANCE_DICT_REUTERS
import relevance_feeback as rf


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