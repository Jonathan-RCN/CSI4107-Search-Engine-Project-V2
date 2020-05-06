"""
Title: Relevance Feedback

Project: CSI4107 Project
Version: Final System
Component: Module 5

Created: 26 Apr 2020

Author: Jonathan Boerger
Status: Completed

Description: This module modifies VSM search results by calculating the Rocchio coefficent for the given search query
based on its relevance data.
This coefficient is then used to modify the document retrieval to create local query expansion.

Limitation:

General references:

    https://github.com/morrisyoung/IR_Relevance_Feedback_Query_Expansion/blob/master/Rocchio.py

"""

from datetime import datetime
import numpy as np
import config
import vsm_retrieval
import linguistic_processor
import relevance_feeback as RF




def rocchio_wrapper(vsm_query, corpus):
    """

    Method called by VSM module to calculate get Rocchio modified weight vecotr.

    This module calls all required methods necesarry to have the required information (q0, Dr, Dnr) to be able to
    calulate the Rocchio modified weight vector then calls the actual method which performs the calculation.
    """
    start_time = datetime.now()
    original_q0_vector = transfrom_query_to_word_vector(vsm_query, corpus)

    # for testing:
    print(get_query_relevance_list(vsm_query, corpus))
    relevant_relevance_list, non_relevant_relevance_list=get_query_relevance_list(vsm_query, corpus)
    #relevant_relevance_list, non_relevant_relevance_list = [0, 1], [3, 4]
    # /for testing
    relevant_Dr_vector_list = tranform_relevance_list_to_document_word_vector_list(relevant_relevance_list, corpus)
    non_relevant_Dnr_vector_list = tranform_relevance_list_to_document_word_vector_list(non_relevant_relevance_list,
                                                                                        corpus)

    result=calculate_rocchio_modified_query_word_vector_weights(original_q0_vector, relevant_Dr_vector_list,
                                                                non_relevant_Dnr_vector_list,
                                                                vsm_query, relevant_relevance_list,
                                                                non_relevant_relevance_list, start_time)
    #print(result)
    return result


def calculate_rocchio_modified_query_word_vector_weights(original_vector, relevant_vector_list,
                                                         non_relevant_vector_list, query, relevant_rl, non_relevant_rl,
                                                         start_time):
    weighted_origional = config.LQE_ROCCHIO_ALPHA * original_vector
    print(len(weighted_origional))

    relevant_vector_list_len = len(relevant_vector_list)
    non_relevant_vector_list_len = len(non_relevant_vector_list)
    if not relevant_vector_list_len: relevant_vector_list_len = 1
    if not non_relevant_vector_list_len: non_relevant_vector_list_len = 1
    beta_weight = config.LQE_ROCCHIO_BETA * (1 / relevant_vector_list_len)
    gamma_weight = config.LQE_ROCCHIO_GAMMA * (1 / non_relevant_vector_list_len)

    relevant_vector_list_sum = np.add.reduce(relevant_vector_list)
    non_relevant_vector_list_sum = np.add.reduce(non_relevant_vector_list)

    positive_feedback = beta_weight * relevant_vector_list_sum
    negative_feedback = gamma_weight * non_relevant_vector_list_sum
    modified_query_word_vector = weighted_origional + positive_feedback - negative_feedback
    modified_query_word_vector = [0 if modified_weight < config.LQE_ROCCHIO_MIN_TOLERANCE
                                  else modified_weight for modified_weight in modified_query_word_vector]

    # print(''.rjust(60, '/'))
    # print('LQE and Rocchio information:')
    # print(''.rjust(60, '='))
    # print(f'Bellow are the heads of the relevant (doc ids: {relevant_rl})'
    #       f' document word vectors (Dr) where each vector is (Dj):')
    # for dj in relevant_vector_list:
    #     print(f'{str(dj[:30])[:57]}...')
    # print(''.rjust(60, '-'))
    # print('These are then added together to a unified vecor:')
    # # print(f'{str(relevant_vector_list_sum[:30])[:57]}...')
    # print(''.rjust(60, '-'))
    # print(
    #     f'A beta factor of {beta_weight} (where beta is {config.LQE_ROCCHIO_BETA}) is then applied to create the positive feedback vector:')
    # print(f'{str(positive_feedback[:30])[:57]}...')
    # print(''.rjust(60, '='))
    # print(f'Bellow are the heads of the non-relevant (doc ids: {non_relevant_rl})'
    #       f' document word vectors (Dnr) where each vector is (Dj):')
    # for dj in non_relevant_vector_list:
    #     print(f'{str(dj[:30])[:57]}...')
    # print(''.rjust(60, '-'))
    # print('These are then added together to a unified vecor:')
    #
    # # print(f'{str(non_relevant_vector_list_sum[:30])[:57]}...')
    # print(''.rjust(60, '-'))
    # print(
    #     f'A beta factor of {gamma_weight} (where beta is {config.LQE_ROCCHIO_GAMMA}) is then applied to create the negative feedback vector:')
    # # print(f'{str(negative_feedback[:30])[:57]}...')
    # print(''.rjust(60, '='))
    # print(f'Bellow is the head of the query ({query}) word vector (q0):')
    # print(f'{str(original_vector[:30])[:57]}...')
    # print(''.rjust(60, '-'))
    print(f'This is then tranformed int new mofied query word vector (qm) via Rocchio algorithm:')
    print(f'{str(modified_query_word_vector[:30])[:57]}...')
    print(''.rjust(60, '='))
    print(f'This took {(datetime.now() - start_time).seconds} seconds to calculate. ')
    print(''.rjust(60, '/'))

    return modified_query_word_vector


def get_query_relevance_list(query, corpus):
    """
    Retreive relevance information from the relevance feedback module
    """
    query_relevance_list = RF.retreive_relevance_as_list(query, corpus)
    # relevant /non relevant
    return query_relevance_list[0], query_relevance_list[1]


def transfrom_query_to_word_vector(query, corpus):
    """
    Transform a search query into a word vector (contaning all indexible words),
    where a 1 indicates that the word was present in the query

    """
    inverted_index = vsm_retrieval.get_inverted_index(corpus)
    # applying linguistic processing s.t. the translated query is the same as index terms
    processed_query = linguistic_processor.linguistic_module(query, config.LINGUISTIC_PARAMS)
    # the word vector is the length of the inverted index for the given corpus
    # It is initialized to zeros
    query_word_vector = np.zeros((len(inverted_index)))
    # iterating over the entire inverted index
    for inverted_index_index, inverted_index_word in enumerate(inverted_index):
        # if a word in the query matches a word in the index, the word vecotr gets a 1
        if inverted_index_word in processed_query:
            query_word_vector[inverted_index_index] = 1

    return query_word_vector


def tranform_relevance_list_to_document_word_vector_list(relevance_list, corpus):
    """
     Takes a list of docId from the relevance feedback (either positive feed back or negative feedback.
    For each doc ID in the list, retrieve its associated document based word vector.

    Return all retrieved word vectors in a list
    """
    inverted_index = vsm_retrieval.get_inverted_index(corpus)
    rl_doc_word_vec_list = []
    # for each doc id in list, get document based word vector
    for doc_id in relevance_list:
        doc_specific_word_vector = transform_doc_id_to_document_word_vector(doc_id, corpus)
        rl_doc_word_vec_list.append(doc_specific_word_vector)
    return rl_doc_word_vec_list


def transform_doc_id_to_document_word_vector(doc_id, corpus):
    """
    Takes a doc ID and produces a word vector containing all the instances of indexible words in the targeted documents
    text.
    The value in the word vector represents the number of occurence of the given word in the target document, where zero
    indicates the given word is not present in the target document.
    """
    inverted_index = vsm_retrieval.get_inverted_index(corpus)
    # word vector is the size of the relevant corpus
    doc_specific_word_vector = np.zeros(len(inverted_index))
    #iterating through the inverted index
    for inverted_index_index, inverted_index_word in enumerate(inverted_index):
        #for a given word in the inverted index, getting the associated docID list
        word_instance_dict = inverted_index[inverted_index_word].get(doc_id)
        # if the target documents doc ID is in the list, extract frequency and added to the word vector
        if word_instance_dict != None:
            doc_specific_word_vector[inverted_index_index] = word_instance_dict['frequency']
        # otherwise word vector gets zero
        else:
            doc_specific_word_vector[inverted_index_index] = 0

    return doc_specific_word_vector
