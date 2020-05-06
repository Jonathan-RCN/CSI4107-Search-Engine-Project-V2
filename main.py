"""
Project: CSI4107 Project
Version: Vanilla System
Component: Main

Created: 30 Jan 2020
Last modified: 13 Feb 2020

Author: Jonathan Boerger & Tiffany Maynard
Status: Complete

Description: Main module - combines all parts of project
"""
from datetime import datetime
import config
#import gui_2
import gui
import corpus_preprocessing_uottawa
import corpus_preprocessing_reuters as corpus_preprocessing_reuters
from build_dictionary_and_index import dictionary_and_inverted_index_wrapper
import relevance_feeback as RF
from text_catgorization_k_nn import get_topics, multipass_wrapper
import bigram_model
import boolean_search


def main():
    """Run search engine and related functions."""
    start_time = datetime.now()
    print(datetime.now())
    corpus = config.UOTTAWA
    print(config.UOTTAWA)
    print(corpus)

    RF.initialize_dicts()

    corpus_preprocessing_uottawa.parse(corpus)
    corpus_preprocessing_reuters.extract_reuters_articles__efficient()
    dictionary_and_inverted_index_wrapper(config.LINGUISTIC_PARAMS, corpus)
    corpus = config.REUTERS
    dictionary_and_inverted_index_wrapper(config.LINGUISTIC_PARAMS, corpus)
    un_speficied_topics_list=get_topics()
    #multipass_wrapper(un_speficied_topics_list,config.KNN_MAX_PASS,config.KNN_SELECTED_METHOD)
    #dictionary_and_inverted_index_wrapper(config.LINGUISTIC_PARAMS, corpus)
    end_time = datetime.now()
    total_time = end_time-start_time
    print(total_time)
    print(datetime.now())

    boolean_queries = ['(*ge AND_NOT (man* OR health*))',
                       '(man* OR health*)',
                       '(statistical OR su*ort)',
                       '(operating AND (system OR platform))',
                       '(query AND processing)',
                       'ps*logy',
                       'leadership']
#    for query in boolean_queries:
#        print(query)
#        print(boolean_search.boolean_search_module(query, corpus))
    vsm_queries = ['operoting system',
                   'computers graphical',
                   'lienar',
                   'business administration',
                   'child psychology',
                   'bayesian network classification']
    # for query in vsm_queries[:1]:
    #     print(query)
    #     print(vsm_retrieval.retrieve(query, corpus))
    # print(boolean_search.boolean_search_module("shareholder AND security", config.REUTERS))
    #gui_2.SearchEngineGUI()
    gui.SearchEngineGUI()





if __name__ == '__main__':
    main()
