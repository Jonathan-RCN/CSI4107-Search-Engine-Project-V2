from datetime import datetime
import csv
import bs4
from nltk.corpus import reuters
from nltk import FreqDist
import config
import gui
import Reteurs.corpus_preprocessing_reuters as corpus_maker
from build_dictionary_and_index import dictionary_and_inverted_index_wrapper
import build_dictionary_and_index



corpus_maker.extract_reuters_articles__efficient()
corpus = config.REUTERS
dictionary_and_inverted_index_wrapper(config.LINGUISTIC_PARAMS, corpus)