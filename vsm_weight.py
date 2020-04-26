"""
Vector Space Model weight calculation

Project: CSI4107 Project
Version: Vanilla System
Component: Module 8a

Created: 09 Feb 2020
Last modified: 09 Feb 2020

Author: Tiffany Maynard
Status: Completed

Description: Include term weights in the index
"""
import math
from collections import Counter

#Adapted from https://medium.com/@fro_g/writing-a-simple-inverted-index-in-python-3c8bcb52169a
def create_inverted_index_vsm(dictionary):
    """Creates an inverted index file with the VSM weights included
    based on the given dictionary doc_id word"""
    vsm_inverted_index = dict(dict())

    # create dictionary with each term and the frequency it appears in each doc
    for term in dictionary:
        if term['word'] in vsm_inverted_index:
            #term already in index, update posting dict
            if term['doc_id'] in vsm_inverted_index[term['word']]:
                 #doc_id already in posting dict, update frequency
                term_freq = vsm_inverted_index[term['word']][term['doc_id']]['frequency']
                vsm_inverted_index[term['word']][term['doc_id']]['frequency'] = term_freq + 1
            else:
                #doc_id not in posting dict, add
                posting = vsm_inverted_index[term['word']]
                posting[term['doc_id']] = ({'frequency':1, 'weight':0})
                vsm_inverted_index[term['word']] = posting
        else:
            #add term to index by creating posting dictionary
            posting = dict()
            posting[term['doc_id']] = ({'frequency':1, 'weight':0})
            vsm_inverted_index[term['word']] = posting

    return set_weights_in_index(vsm_inverted_index)

def set_weights_in_index(inv_index):
    """Go through inverted index and set the tf-idf weights."""
#Count of doc_ids adapted from
#https://stackoverflow.com/questions/39353428/count-of-unique-values-in-nested-dict-python
    seen_doc_ids = Counter()
    for data in inv_index.values():
        seen_doc_ids += Counter(data.keys())
    num_docs = len(seen_doc_ids.items())

    for term in inv_index:
        for doc_id in inv_index[term]:
            weight = calc_tfidf_weight(num_docs,
                                       inv_index[term][doc_id]['frequency'],
                                       len(inv_index[term].keys()))
            inv_index[term][doc_id]['weight'] = weight
    return inv_index

def vsm_inv_index_tocsv(inv_index, csv_filename):
    """Writes the inverted index with weights to csv"""
    with open(csv_filename, 'w') as file:
        [file.write('{0},{1}\n'.format(key, value)) for key, value in inv_index.items()]

def calc_tfidf_weight(num_docs, t_f, d_f):
    """Calculate tf-idf weight for a given num_docs
    tf (term frequency) and df (document frequency)
    using tf-idf weight version from slide 21 of Winter2020-CSI4107-VSM.pdf"""
    return math.log10(1+t_f) * math.log10(num_docs/(d_f or num_docs))
