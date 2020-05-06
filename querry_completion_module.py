"""
Title: Query Completion Module

Project: CSI4107 Project
Version: Final System
Component: Module 2

Created: 25 Apr 2020
Last modified: 27 Apr 2020

Author: Jonathan Boerger
Status: Completed

Description: This module translate a bigram index into a use predictive tool. This model extracts the n-best predictions
from the given query word where n is a configurable (in 'config.py') limit to number of bigrams returned.

The generated word-completion pairs are corpus independant and will provide the same query completion functionality
regardless which corpus is being searched.

Furthermore, this module interfaces with the GUI (module 7) to provide query completion predictions in the search engine.

Limitation:
    The word-prediction pairs are static therefore to for changes to be reflected, the search engine needs to be restarted.

    In the interaction with the GUI (module 7), the query completion only applies to the first word. Subsequent words
    do not benefit from the QCM.

General references:
    As detailled in the project report, I was unable to implement module 7. Therefore, I have adapted Tiffany Maynard
    GUI for her version of this project to work with this module. As a result, some methods are structured similarily
    to allow for intergration.
"""


import ast
import csv
import config
import os

COMPLETION_LIST=[]

def get_bigram_from_csv(corpus):
    bigram_csv_file_name=config.CORPUS[corpus]['bigram_file']
    usable_bigram_dict=dict()
    if os.path.exists(bigram_csv_file_name):
        with open(bigram_csv_file_name, 'r') as file:
            csv.field_size_limit(100000000)
            reader = csv.reader(file)
            for row in reader:
                if row != []:
                    usable_bigram_dict[row[0]] = ast.literal_eval(row[1])
        return usable_bigram_dict

    else:
        print(f'There is no available bigram model currently available for {corpus}')
        return {}



def get_n_best_completion_pairs(n_gram_dict):
    '''

    Selecting and returning the n-best word-completion pairs for all words in the bigram index.
    '''
    for primary_word in n_gram_dict:
        secondary_word_list=list(n_gram_dict[primary_word])
        top_n_word_list=secondary_word_list[:config.QCM_MAX_NO_WORD_SUGGESTED]
        for secondary_word in top_n_word_list:
            completion_pair=f'{primary_word} {secondary_word}'
            global COMPLETION_LIST
            COMPLETION_LIST.append(completion_pair)

def translate_completion_list_to_static_csv(completion_list):
    """
    Taking the generated word-completion pairs and saving them (statically) to a csv file such that they can be used by
    the search engine to perform QCM.
    """
    csv_filename="qcm_complation_pair_list.csv"
    s = ','
    completion_string = s.join(completion_list)
    #print(completion_string.split(','))
    with open(csv_filename, 'w', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(completion_string.split(','))

def qcm_wrapper_creation():
    """
    Determine the n-best word-completion pairs from both the uOttawa bigram index and Reuters bigraph index.
    """
    uottawa_n_gram_dict=get_bigram_from_csv(config.UOTTAWA)
    get_n_best_completion_pairs(uottawa_n_gram_dict)
    reuter_n_gram_dict=get_bigram_from_csv(config.REUTERS)
    get_n_best_completion_pairs(reuter_n_gram_dict)
    global COMPLETION_LIST
    translate_completion_list_to_static_csv(COMPLETION_LIST)

def qcm_completion_list_access():
    """
    Module 7 intergration.
    Return the word-completion pairs to the GUI when requested.
    """
    global COMPLETION_LIST
    if COMPLETION_LIST !=[]:
        return COMPLETION_LIST
    else:
        csv_filenmae="qcm_complation_pair_list.csv"
        if os.path.exists(csv_filenmae):
            with open(csv_filenmae, newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                qcm_complation_pair_list = list(reader)
            return qcm_complation_pair_list[0]
        else:
            print(f'There is no available QCM completion pair list currently available')
            return []


