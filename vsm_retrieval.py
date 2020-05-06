"""
Vector Space Model retrieval

Project: CSI4107 Project
Version: Vanilla System
Component: Module 8b

Created: 09 Feb 2020
Last modified: 27 Apr 2020

Author: Tiffany Maynard

Status: Complete

Description: Implement Vector Space Model from retrieval

Modification:
    Added functionaly to implement local query expansion (via rocchio), suport for limmiting searches to sepific
    topics and, support for text classification.
"""

from heapq import nlargest
import ast
import numpy as np
import config
import linguistic_processor
import text_catgorization_k_nn
import relevance_feeback as RF
from  local_query_expansion_rocchio import rocchio_wrapper

#import vsm_weight

INVERTED_INDEX = {}
INVERTED_INDEX_CORPUS = ""

def convert_query(query):
    """Convert the query string to a vector."""
    return linguistic_processor.linguistic_module(query, config.LINGUISTIC_PARAMS)

def similarity(doc_list, query_list):
    """Calculate the cosine similarity for the two vectors."""
    #adapted Method 2 from https://stackoverflow.com/a/43943429
    doc_vector = np.array(doc_list)
    query_vector = np.array(query_list)
    doc_norm = doc_vector / np.linalg.norm(doc_vector, axis=0)
    query_norm = query_vector / np.linalg.norm(query_vector, axis=0)
    return np.dot(doc_norm, query_norm)

def retrieve(query, corpus, topic):
    """
    VSM query wrapper that interfaces with gui.
    If there is relevance information for the query, rocchio weights is used

    """
    # print(f'The selected topic for this query is; {topic}')
    print(RF.retreive_relevance_as_list(query,corpus))
    if RF.retreive_relevance_as_list(query,corpus):
        return rocchio_retrival(query, corpus, topic)
    else:
        # print('standard')
        return standard_retreival(query, corpus, topic)

def rocchio_retrival(query, corpus, topic):
    """
    VSM retrieval where query vector is adjusted based on relevance feedback.
    """

    modified_query_vector = rocchio_wrapper(query, corpus)
    score = dict()

    # docs = shortlist(query, corpus, topic)
    #print(modified_query_vector)
    docs = roochio_shortlist(modified_query_vector, corpus, topic)
    print(docs)
    for doc_id in docs:
        score[doc_id] = similarity(docs[doc_id], modified_query_vector)
    # Adapted from https://www.geeksforgeeks.org/python-n-largest-values-in-dictionary/

    klargest = nlargest(config.K_RETRIEVAL, score, key=score.get)
    # Adapted from https://stackoverflow.com/a/38218662
    return [(x, score[x]) for x in klargest]

def standard_retreival(query, corpus, topic):
    """
    Standard vsm retrival method where local relevance is not factored in result relevance socre.
    :param query:
    :param corpus:
    :param topic:
    :return:
    """
    # create list of 1's for each word in query, assumes equal weighting for each term
    query_ones = [1 for x in range(len(convert_query(query)))]
    score = dict()
    docs = shortlist(query, corpus, topic)
    for doc_id in docs:
        score[doc_id] = similarity(docs[doc_id], query_ones)
    # Adapted from https://www.geeksforgeeks.org/python-n-largest-values-in-dictionary/

    klargest = nlargest(config.K_RETRIEVAL, score, key=score.get)
    # Adapted from https://stackoverflow.com/a/38218662
    return [(x, score[x]) for x in klargest]

def knn_retrieve(query):
    """
    Retreive the k nearest neighbhors where distance is asses based on VSM relevance score
    Functionally the same as standard vsm retrival however, only return the doc ids.

    """

    #create list of 1's for each word in query, assumes equal weighting for each term
    query_ones = [1 for x in range(len(convert_query(query)))]
    score = dict()
    docs = shortlist(query, config.REUTERS,'all_topics')
    for doc_id in docs:
        score[doc_id] = similarity(docs[doc_id], query_ones)
    #Adapted from https://www.geeksforgeeks.org/python-n-largest-values-in-dictionary/

    klargest = nlargest(config.K_RETRIEVAL+1, score, key=score.get)
    #Adapted from https://stackoverflow.com/a/38218662
    nearest_neighbhors=[x for x in klargest]
    return nearest_neighbhors[1:]


def shortlist(query, corpus, topic):
    """Create shortlist of docs from inv_index based only on those that have at
     least one search term from the query."""
    inv_index = get_inverted_index(corpus)
    doc_shortlist = dict()
    query_word_list = convert_query(query)
    weight_list_len = len(query_word_list)
    if corpus == config.REUTERS:
        topic_docs = list(map(int, text_catgorization_k_nn.get_topic_information(topic)))
    else:
        topic_docs = list(range(0, 663))
    for index, word in enumerate(query_word_list):
        if word in inv_index:
            #allow for queries that contain words not in the corpus
            #limiting the corpus search to only documents of selected topics
            for doc_id in set(inv_index[word]).intersection(set(topic_docs)):
                if doc_id in doc_shortlist:
                    #doc already added, just update weight entry for this word
                    doc_shortlist[doc_id][index] = inv_index[word][doc_id]['weight']
                else:
                    #doc not added yet add doc_id to shortlist,
                    #initialize list to 0s for all words in query
                    #update weight entry for current word
                    entry = [0 for x in range(weight_list_len)]
                    entry[index] = inv_index[word][doc_id]['weight']
                    doc_shortlist[doc_id] = entry

    return doc_shortlist

def roochio_shortlist(modified_query_vector, corpus,topic):
    """Modifies the shortlist method to function with the slightly different input for rocchio search
    (query vector vs query string).
    This methods returns the same product as the standard shortlist"""
    #print(modified_query_vector)
    inv_index = get_inverted_index(corpus)
    doc_shortlist = dict()
    vector_len = len(modified_query_vector)
    word_list = list(inv_index.keys())
    if corpus == config.REUTERS:
        topic_docs = list(map(int, text_catgorization_k_nn.get_topic_information(topic)))
    else:
        topic_docs = list(range(0, 663))
    for index, weight in enumerate(modified_query_vector):
        word=word_list[index]
        if word in inv_index:
            # allow for queries that contain words not in the corpus
            # limiting the corpus search to only documents of selected topics
            for doc_id in set(inv_index[word]).intersection(set(topic_docs)):
                # print(set(inv_index[word]).intersection(set(topic_docs)))
                if doc_id in doc_shortlist:

                    # doc already added, just update weight entry for this word
                    print(word)
                    print(doc_id)
                    print(index)
                    print(doc_shortlist)
                    print(inv_index[word][doc_id]['weight'])
                    print(doc_shortlist[doc_id][index])
                    doc_shortlist[doc_id][index] = inv_index[word][doc_id]['weight']
                else:
                    # doc not added yet add doc_id to shortlist,
                    # initialize list to 0s for all words in query
                    # update weight entry for current word
                    entry = [np.zeros(vector_len)]
                    entry[index] = inv_index[word][doc_id]['weight']
                    doc_shortlist[doc_id] = entry

    return doc_shortlist



def get_inverted_index(corpus):
    """Wrapper to allow reading only once from csv file"""
    global INVERTED_INDEX
    global INVERTED_INDEX_CORPUS
    if INVERTED_INDEX and corpus == INVERTED_INDEX_CORPUS:
        return INVERTED_INDEX
    INVERTED_INDEX_CORPUS = corpus
    INVERTED_INDEX = read_inverted_index_from_csv(corpus)
    return INVERTED_INDEX

def read_inverted_index_from_csv(corpus):
    """Read in the inverted index file from disk."""
    csv_filename = config.CORPUS[corpus]['inverted_index_file']

    new_data_dict = {}
    with open(csv_filename, 'r') as data_file:
        for row in data_file:
            row = row.strip().split(",", 1)
            new_data_dict[row[0]] = ast.literal_eval(row[1])
    return new_data_dict
