"""
Title: Dictionary and Inverted Index Builder Module

Project: CSI4107 Project
Version: Vanilla System
Component: Module 3 & 4 + supporting methods for module 7

Created: 30 Jan 2020
Last modified: 13 Apr 2020

Author: Jonathan Boerger
Modified by: Tiffany Maynard
Status: Complete

Description: This takes a corpus, applies linguistic processing on the documents within the corpus
            and creates an IR dictionary which is then used to build an inverted index and bigraph
            index in csv file format.

"""
import csv
import os
import xml.etree.ElementTree as xml
from collections import Counter
from collections import OrderedDict
from collections import defaultdict
import pandas as pd
from nltk.corpus import reuters
from nltk import FreqDist
from linguistic_processor import linguistic_module, bigraph_splitter
import vsm_weight
import config
import Reteurs.text_categorization as text_categorization
import Reteurs.bigram_model as bigram_model
import Reteurs.Querry_Completion as QCM

def __build_dictionary(corpus_filename, linguistic_processing_parameters):
    """
    This private method transform a corpus of documents into an IR dictionary. The documents undergo
    linguistic pre-processing prior to forming the dictionary.

    :param corpus_filename: Name of the corpus
    :param linguistic_processing_parameters: Dictionary (data struct.) specifying which linguistic
        process to apply to the text; see linguistic_processor.linguistic_module() for exact format
    :return: IR dictionary containing all words in the corpus associated with their
            respective document
    """
    dictionary = []
    parser = xml.XMLParser(encoding="utf-8")
    tree = xml.parse(corpus_filename, parser=parser)
    root = tree.getroot()
    fdist = FreqDist(w.lower() for w in reuters.words())
    for course in root:
        doc_id = int(course.get('doc_id'))
        course_id = course[0].text
        processed_text = linguistic_module(course[2].text, linguistic_processing_parameters)

        for words in processed_text:
            #if corpus_filename == "reuters_corpus.xml" and fdist[words] > 1:
                #remove hapax for reuters collection
            tag = {"course_id": course_id, "doc_id": doc_id, "word": words}
            dictionary.append(tag)
    return dictionary

def __build_spelling_dictionary(corpus_filename, linguistic_processing_parameters):
    """
    This private method transform a corpus of documents into a spelling dictionary.
    The documents undergo linguistic processing prior to forming the dictionary
    except for stemming and lemmatization

    :param corpus_filename: Name of the corpus
    :param linguistic_processing_parameters: Dictionary (data struct.) specifying which linguistic
        process to apply to the text; see linguistic_processor.linguistic_module() for exact format
    :return: spelling dictionary containing all words in the corpus associated with their frequency
    """
    word_list = []
    tree = xml.parse(corpus_filename)
    root = tree.getroot()
    linguistic_revised = linguistic_processing_parameters.copy()
    linguistic_revised["do_stemming"] = False
    linguistic_revised["do_lemming"] = False
    for doc in root:
        processed_text = linguistic_module(doc[2].text, linguistic_revised)
        for word in processed_text:
            if not any(char.isdigit() for char in word):
                word_list.append(word)
    #sort by word frequency from https://stackoverflow.com/a/613218
    return OrderedDict(sorted(Counter(word_list).items(), reverse=True, key=lambda kv: kv[1]))

def __create_inverted_index(dictionary):
    """
    This private method takes an IR dictionary and creates an inverted index which includes
    term frequency and tfidf weights

    :param dictionary: List of dictionaries (data structure) containing word-docID association
    :return: Inverted index as a dict of dicts (data structure)
    """

    return vsm_weight.create_inverted_index_vsm(dictionary)


def __inverted_index_csv(inverted_index, inverted_index_filename):
    """
    This private methods creates a csv file for the inverted index and fills it

    :param inverted_index: The inverted index (in dict form)
    :param inverted_index_filename: The name of the inverted index csv file
    :output: A csv file containing the inverted index
    """
    vsm_weight.vsm_inv_index_tocsv(inverted_index, inverted_index_filename)


def __inverted_index_csv_creator(ii_filename):
    """
    This private methods creates a csv which will be used to store the inverted index.

    :ii_filename: file name for the csv file
    :return: an empty csv file
    """
    # since this method may be called when the csv file needs to be re-created
    # the methods deletes the existing
    try:
        os.unlink(ii_filename)
    except FileNotFoundError:
        pass

    with open(ii_filename, 'w', newline='', encoding='utf-8') as file:
        header = ["Word", "Postings"]
        writer = csv.writer(file)
        writer.writerow(header)


def __linguistic_processing_parameter_csv_creator(lpp_file):
    """
    This private methods creates a csv which will be used to store the linguistic processing
    parameter information

    :param lpp_file: file name for the csv file
    :return: an empty csv file
    """
    # since this method may be called when the csv file needs to be re-created
    # the methods deletes the existing
    try:
        os.unlink(lpp_file)
    except FileNotFoundError:
        pass

    with open(lpp_file, 'w', newline='', encoding='utf-8') as file:
        header = ["Para1", "Para2", "Para3", "Para4", "Para5", "Para6", "Para7", "Para8", ]
        writer = csv.writer(file)
        writer.writerow(header)


def __linguistic_processing_parameters_csv(linguistic_processing_parameters_dictionary,
                                           lpp_csv_file):
    """
    This private method creates and fills a csv file with the linguistic processing parameters

    :param linguistic_processing_parameters_dictionary: The dictionary (data structure) containing
    the LPP
    :param lpp_csv_file: the LPP csv file
    :return: a csv file containing LPP info
    """
    __linguistic_processing_parameter_csv_creator(lpp_csv_file)
    to_append = ''
    for key in linguistic_processing_parameters_dictionary:
        to_append = to_append + f' {linguistic_processing_parameters_dictionary[key]}'

    with open(lpp_csv_file, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(to_append.split())


def __linguistic_processor_parameters_validator(lpp_csv_file, lpp_dictionary):
    """
    This private method compared the inverted index LPP to the currently specified LPP
    for any differences

    :param lpp_csv_file: the csv file containing the LPP for the current inverted index csv
    :param lpp_dictionary: a dictionary (data structure) containing the current LPP
    :return: -1 if there is a difference between the LPP found in the csv file and those
                specified in the dictionary
            1 if the csv file and dictionary match
    """
    previous_linguistic_settings = []
    current_linguistic_settings = []
    data = pd.read_csv(lpp_csv_file)
    for index in range(0, 8):
        previous_linguistic_settings.append(data.iloc[0, index])
    for key in lpp_dictionary:
        current_linguistic_settings.append(lpp_dictionary[key])
    for index in range(0, 8):
        if current_linguistic_settings[index] == previous_linguistic_settings[index]:
            pass
        else:
            return -1
    return 1

def __bigraph_index_creator(spelling_dict):
    """
    This private method creates a bigraph index based on the spelling dictionary.


    :return: A list of list containing the bigraph and its associated words
    """

    bigraph_dict = defaultdict(set)
    for word in spelling_dict:
        bigraph_list = bigraph_splitter(word)
        for bigraph in bigraph_list:
            #if bigraph[0] in bigraph_dict:
            bigraph_dict[bigraph[0]].add(word)
            #else:
                #bigraph not in bigraph_dict, add new list
        #        word_set = set()
        #        word_set.add(word)
        #        bigraph_dict[bigraph[0]] = word_set

    return bigraph_dict

def __bigraph_index_csv_creator(bi_filename):
    """
    This private method creates a csv file to store the bigraph index.

    :param bi_filename: filename for the bigraph index csv file
    :return: an empty csv file
    """
    # since this method may be called when the csv file needs to be re-created
    # the methods deletes the existing
    try:
        os.unlink(bi_filename)
    except FileNotFoundError:
        pass

    with open(bi_filename, 'w', newline='', encoding='utf-8') as file:
        header = ["Bigraph", "Word List"]
        writer = csv.writer(file)
        writer.writerow(header)

def __bigraph_index_csv(filename, bigraph_index):
    """
    This private methods inputs the bigraph index into its csv file.

    :param bi_filename: The file name of the bigraph index csv file
    :param bigraph_index: The list contain all bigrams
    :return: A csv containing the bigraph index

    """
    __bigraph_index_csv_creator(filename)
    with open(filename, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for key, value in bigraph_index.items():
            writer.writerow([key, value])

def __spelling_dictionary_csv_creator(filename):
    """
    This private method creates a csv file to store the spelling dictionary.

    :param filename: filename for the spelling dictionary csv file
    :return: an empty csv file
    """
    # since this method may be called when the csv file needs to be re-created
    # the methods deletes the existing
    try:
        os.unlink(filename)
    except FileNotFoundError:
        pass

    with open(filename, 'w', newline='', encoding='utf-8') as file:
        header = ["word", "frequency"]
        writer = csv.writer(file)
        writer.writerow(header)

def __spelling_dictionary_csv(filename, spelling_dictionary):
    """
    This private method writes the spelling dictionary to the csv file.

    :param filename: The file name of the spelling dictionary csv file
    :param spelling_dictionary: The dictionary containing all words and frequencies
    :return: A csv containing the spelling dictionary

    """
    __spelling_dictionary_csv_creator(filename)

    with open(filename, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for key, value in spelling_dictionary.items():
            writer.writerow([key, value])





def dictionary_and_inverted_index_wrapper(linguistic_control_dictionary, corpus):
    """
    This is the public method for the build dictionary, inverted index and bigraph index module.
    This method integrates all methods required to build the IR dictionary and its
    corresponding inverted index and bigraph index.
    Additionally, it also checks to see if the inverted file already exists, if it does
    the method carries on without recreating the index.
    Lastly, in the event that the linguistic pre-processing parameters are changed, regardless
    if the inverted index already exists, will create new indexes to reflect
    the changes in dictionary resulting from different linguistic processing.



    :param linguistic_control_dictionary: The dictionary which specifies which linguistic
        processing modules should be used to create the inverted index.
    :param inverted_index_filename: The inverted index file name
     :param corpus_filename: The document corpus filename
     :param bigraph_filename: The bigraph index filename
    :param lp_parameter_filename: The linguistic processing control file
    :return: A csv file containing the inverted index and bigraph index
    """
    inverted_index_filename = config.CORPUS[corpus]['inverted_index_file']
    corpus_filename = config.CORPUS[corpus]['corpusxml']
    lp_parameter_filename = config.CORPUS[corpus]['lpp_file']
    bigraph_filename = config.CORPUS[corpus]['bigraph_file']
    spelling_filename = config.CORPUS[corpus]['spelling_file']

    def create_index():
        ir_dictionary = __build_dictionary(corpus_filename, linguistic_control_dictionary)
        inverted_index = __create_inverted_index(ir_dictionary)
        __inverted_index_csv(inverted_index, inverted_index_filename)
        spelling_dictionary = __build_spelling_dictionary(corpus_filename,
                                                          linguistic_control_dictionary)
        __spelling_dictionary_csv(spelling_filename, spelling_dictionary)
        bigraph_index = __bigraph_index_creator(spelling_dictionary)
        __bigraph_index_csv(bigraph_filename, bigraph_index)
        __linguistic_processing_parameters_csv(linguistic_control_dictionary, lp_parameter_filename)
        bigram_model.create_bigram_model(corpus)

    # if corpus == config.REUTERS and not os.path.exists(config.CORPUS[corpus]['doc_by_topic']):
    #     text_categorization.doc_id_by_topic()

    if os.path.exists('Reteurs/qcm_complation_pair_list.csv'):
        pass
    else:
        QCM.qcm_wrapper_creation()

    #The required files dont exits -> create them
    if not os.path.exists(inverted_index_filename)  \
            or not os.path.exists(lp_parameter_filename) \
            or not os.path.exists(bigraph_filename) \
            or not os.path.exists(spelling_filename)\
            or not os.path.exists(config.CORPUS[corpus]['bigram_file']):

        print("Not all files exist which need to exist thus we are creating them")
        create_index()
        return



    check_val = __linguistic_processor_parameters_validator(lp_parameter_filename,
                                                            linguistic_control_dictionary)

    if check_val == -1:
        # the required files exist BUT changes to the LPP -> create a new inverted index
        print("Inverted index already exists, however there has been a change in LP settings, thus "
              "recalculating it")
        create_index()
    else:
        # the required files exist & no changes to the LPP -> carry on
        print(corpus + "inverted index for these LP setting already exists.")

    return
