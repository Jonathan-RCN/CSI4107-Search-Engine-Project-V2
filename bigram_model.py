"""
Title: Bigram Model Module

Project: CSI4107 Project
Version: Final System
Component: Module 1

Created: 25 Apr 2020
Last modified: 27 Apr 2020

Author: Jonathan Boerger
Status: Completed

Description: This module creates a bigram index for all words in the specified corpus. The bigram index is created
from  the sum of all indexable text in the corpus. Bigrams are then isolated for each indexible word and
probabilities are subsequently calculated.

Linguistic pre-processing (with the exception of steeming/lemming) is applied to the corpus prior to creating
bigraph index. The spefics of the linguistic pre-processing can be confrigured in the 'config.py' file.

Limitation:
    All text is joined together into one massive list of word tokens. This created bigraphm pairs between the last word
    of an article and the first word of the next article that would not have existed if another method was employed.

General reference:
    "https://towardsdatascience.com/introduction-to-language-models-n-gram-e323081503d9"

"""

import csv
import operator
from nltk import collections, ngrams, FreqDist
import config
from linguistic_processor import linguistic_module
import xml.etree.ElementTree as ET
from tqdm import tqdm
from datetime import datetime




def create_bigram_model(corpus):
    n_gram_count = 2
    n_gram_list = []
    model = dict(dict())
    corpus_filename = config.CORPUS[corpus]['corpusxml_bigram']
    tree = ET.parse(corpus_filename)
    root = tree.getroot()
    count = 1
    complete_word_list = []
    for index in root:
        count += 1
    # compilling all indexible text in corpus and applying LPP to this text
    with tqdm(total=count) as pbar:
        for document in root:
            text = linguistic_module(document[2].text, config.BIGRAM_MODEL_LINGUISTIC_PARAMS)
            for words in text:
                complete_word_list.append(words)
            pbar.update(1)
    # getting the frequency distribution the words in the corpus in relation to corpus as a whole
    fdist = FreqDist(w.lower() for w in complete_word_list)
    # spliting the corpus into bigrams
    n_grams = ngrams(complete_word_list, n_gram_count)

    for grams in n_grams:
        n_gram_list.append(grams)

    # Adapted from https://www.kaggle.com/rtatman/tutorial-getting-n-gram\
    # Getting the number of occurences of each bigram
    n_gram_freq = collections.Counter(n_gram_list)
    # /Adapted

    with tqdm(total=n_gram_freq.__len__()) as pbar:
        for gram in n_gram_freq.items():
            bigram_word_1 = gram[0][0]
            # filtering out words that do not meet the minimum threshold in relation to entire corpus
            if fdist[bigram_word_1] < config.BIGRAM_MODEL_REQUIRED_MIN_FREQ[corpus]:
                pbar.update(1)
                continue
            bigram_word_2 = gram[0][1]
            bigram_count = gram[1]

            # filtering out bigrams that do not meet the minimum threshold. Currently ommited as it negatively effects
            # quality of the biagram model predictive power.
            # if bigram_count < config.BIGRAM_MODEL_REQUIRED_MIN_FREQ:
            #     pbar.update(1)
            #     continue
            # Adpated from https://medium.com/analytics-vidhya/a-comprehensive-guide-to-build-your-own-language-model-in-python-5141b3917d6d
            # adding the bigram and its occurence number to bigram dictonary which acts as the model
            if bigram_word_1 not in model:
                model[bigram_word_1] = dict()
                model[bigram_word_1][bigram_word_2] = bigram_count
            else:
                model[bigram_word_1][bigram_word_2] = bigram_count
            pbar.update(1)
    # determining the weights of each bigram pair for given word
    for bigram_word_1 in model:
        total_count = float(sum(model[bigram_word_1].values()))
        for bigram_word_2 in model[bigram_word_1]:
            model[bigram_word_1][bigram_word_2] /= total_count
    # writting the bigram model to csv s.t. there is not a need to recalculate this multiple times.
    n_gram_to_csv(model, corpus)


def print_n_gram(n_gram_model):
    for key, value in n_gram_model.items():
        value = dict(sorted(value.items(), key=operator.itemgetter(1), reverse=True))
        print(key, value)


def n_gram_to_csv(n_gram_model, corpus):
    csv_filename = config.CORPUS[corpus]['bigram_file']
    with open(csv_filename, 'w', encoding='utf-8') as file:
        writer = csv.writer(file)
        for key, value in n_gram_model.items():
            value = dict(sorted(value.items(), key=operator.itemgetter(1), reverse=True))
            writer.writerow([key, value])


"Initial emplementiations || Functional but inneficient"
# """Version 2"""
# n_gram_count = 2
# n_gram_list = []
# model = dict(dict())
# corpus_filename = config.CORPUS[corpus]['corpusxml']
# tree = ET.parse(corpus_filename)
# root = tree.getroot()
# count=1
# for index in root:
#     count+=1
# with tqdm(total=count) as pbar:
#     for document in root:
#
#         text = linguistic_module(document[2].text, config.BIGRAM_MODEL_LINGUISTIC_PARAMS)
#         n_grams = ngrams(text, n_gram_count)
#         for grams in n_grams:
#             n_gram_list.append(grams)
#         # Adapted from https://www.kaggle.com/rtatman/tutorial-getting-n-gram
#         n_gram_freq = collections.Counter(n_gram_list)
#         # /Adapted
#
#         for gram in n_gram_freq.items():
#             bigram_word_1 = gram[0][0]
#             bigram_word_2 = gram[0][1]
#             bigram_count = gram[1]
#             if bigram_count < config.BIGRAM_MODEL_REQUIRED_MIN_FREQ:
#                 continue
#             # Adpated from https://medium.com/analytics-vidhya/a-comprehensive-guide-to-build-your-own-language-model-in-python-5141b3917d6d
#             if bigram_word_1 not in model:
#                 model[bigram_word_1] = dict()
#                 model[bigram_word_1][bigram_word_2] = bigram_count
#             else:
#                 model[bigram_word_1][bigram_word_2] = bigram_count
#         pbar.update(1)
# with tqdm(total=count) as pbar:
#     for bigram_word_1 in model:
#         total_count = float(sum(model[bigram_word_1].values()))
#         for bigram_word_2 in model[bigram_word_1]:
#             model[bigram_word_1][bigram_word_2] /= total_count
#         pbar.update(1)
# # /Adapted
#
# #print_n_gram(model)
# n_gram_to_csv(model,corpus)


# '''Version 1'''
# corpus_filename = config.CORPUS[config.UOTTAWA]['corpusxml']
# n = 2
# n_gram_list=[]
# stops = set(stopwords.words("english"))
# tree = ET.parse(corpus_filename)
# root = tree.getroot()
# # for child in root:
# #     print(child[2].text)
#
# with open(corpus_filename, 'rb') as f:
#     data = f.read()
#     soup = bs4.BeautifulSoup(data, 'html.parser')
#     courses = soup.findAll("course_description")
#     for course in courses:
#         LINGUISTIC_PARAMS = {"do_contractions": True,
#                              "do_normalize_hyphens": True,
#                              "do_normalize_periods": True,
#                              "do_remove_punctuation": True,
#                              "do_case_fold": True,
#                              "do_stop_word_removal": True,
#                              "do_stemming": False,
#                              "do_lemming": False}
#         text=linguistic_module(course.text,LINGUISTIC_PARAMS)
#
#         # token_list=[]
#         # for token in text:
#         #     if token not in stops:
#         #         token_list.append(token)
#
#         sixgrams = ngrams(text, n)
#
#         for grams in sixgrams:
#           #print (grams)
#           n_gram_list.append(grams)
#
# gram_freq = collections.Counter(n_gram_list)
#
# model = dict(dict())
#
# for grm in gram_freq.items():
#     bigram_word_1=grm[0][0]
#     bigram_word_2=grm[0][1]
#     bigram_count=grm[1]
#     if bigram_count<config.BIGRAM_MODEL_REQUIRED_MIN_FREQ:
#         continue
#
#     if bigram_word_1 not in model:
#         model[bigram_word_1]=dict()
#         model[bigram_word_1][bigram_word_2]=bigram_count
#     else:
#         model[bigram_word_1][bigram_word_2] = bigram_count
#
#
#
#
#
# for w1 in model:
#     total_count = float(sum(model[w1].values()))
#     for w2 in model[w1]:
#         model[w1][w2] /= total_count
#
# for key, value in model.items():
#     print(f' {key}*2')
#     value=dict(sorted(value.items(), key=operator.itemgetter(1),reverse=True))
#     for key2, value2 in value.items():
#         print(f'       --> {key2} --> {value2}')
#
#
# #
# print('/////////////////////////////////////////////////////////////////////')
