import csv
import operator
from nltk import collections, ngrams, FreqDist
import config
from linguistic_processor import linguistic_module
import xml.etree.ElementTree as ET
from tqdm import tqdm
from datetime import datetime
"https://towardsdatascience.com/introduction-to-language-models-n-gram-e323081503d9"

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
    with tqdm(total=count) as pbar:
        for document in root:
            text = linguistic_module(document[2].text, config.BIGRAM_MODEL_LINGUISTIC_PARAMS)
            for words in text:
                complete_word_list.append(words)
            pbar.update(1)

    fdist = FreqDist(w.lower() for w in complete_word_list)
    n_grams = ngrams(complete_word_list, n_gram_count)

    for grams in n_grams:
        n_gram_list.append(grams)

    # Adapted from https://www.kaggle.com/rtatman/tutorial-getting-n-gram
    n_gram_freq = collections.Counter(n_gram_list)
    # /Adapted

    with tqdm(total=n_gram_freq.__len__()) as pbar:
        for gram in n_gram_freq.items():
            bigram_word_1 = gram[0][0]
            if fdist[bigram_word_1] < config.BIGRAM_MODEL_REQUIRED_MIN_FREQ[corpus]:
                pbar.update(1)
                continue
            bigram_word_2 = gram[0][1]
            bigram_count = gram[1]
            # if bigram_count < config.BIGRAM_MODEL_REQUIRED_MIN_FREQ:
            #     pbar.update(1)
            #     continue
            # Adpated from https://medium.com/analytics-vidhya/a-comprehensive-guide-to-build-your-own-language-model-in-python-5141b3917d6d
            if bigram_word_1 not in model:
                model[bigram_word_1] = dict()
                model[bigram_word_1][bigram_word_2] = bigram_count
            else:
                model[bigram_word_1][bigram_word_2] = bigram_count
            pbar.update(1)

    for bigram_word_1 in model:
        total_count = float(sum(model[bigram_word_1].values()))
        for bigram_word_2 in model[bigram_word_1]:
            model[bigram_word_1][bigram_word_2] /= total_count

    n_gram_to_csv(model, corpus)

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

def print_n_gram(n_gram_model):
    for key, value in n_gram_model.items():
        value = dict(sorted(value.items(), key=operator.itemgetter(1), reverse=True))
        print(key,value)


def n_gram_to_csv(n_gram_model, corpus):
    csv_filename = config.CORPUS[corpus]['bigram_file']
    with open(csv_filename, 'w', encoding='utf-8') as file:
        writer = csv.writer(file)
        for key, value in n_gram_model.items():
            value = dict(sorted(value.items(), key=operator.itemgetter(1), reverse=True))
            writer.writerow([key, value])






#"""Version 2"""
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


#'''Version 1'''
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

