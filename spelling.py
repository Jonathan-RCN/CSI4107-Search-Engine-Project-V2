"""
Spelling correction with weighted edit distance

Project: CSI4107 Project
Version: Vanilla System
Component: Module 9

Created: 27 Jan 2020
Last modified: 13 Feb 2020

Author: Tiffany Maynard
Status: Complete

Description: Provide suggestions for corrected words to the user
"""
import csv
import collections
import unicodedata
from heapq import nsmallest
import numpy
import config
from linguistic_processor import punctuation_remover

#Empty globals to store spelling dictionary so it is only read once form csv
SPELLING_DICT = {}
SPELLING_CORPUS = ""

def suggest_words(given_words, corpus):
    """Returns list of suggested words based on a given word
       assumes first letter is correct"""

    word_list = given_words.replace('*', ' ').replace('(', '( ').replace(')', ' )').split()
    spelling_dict = get_spelling_dictionary(corpus)
    words_not_in_dic = list_words_not_in_dictionary(word_list, spelling_dict)
    first_letter_dict = make_first_letter_dict(spelling_dict)

    suggestions = []
    #dict to hold corrections for each mispelled word
    corrections = dict()
    for given_word in words_not_in_dic:
        #only suggest corrections for words not found in spelling dictionary
        ed_score = dict()
        for word in first_letter_dict[given_word[0]]:
            #assume first letter is correct
            #and compare only to words that start with same letter
            ed_score[word] = edit_distance(word, given_word)
        if len(given_word) > 1:
            for word in first_letter_dict[given_word[1]]:
                #assume second letter should be first letter
                #and compare only to words that start with same letter
                ed_score[word] = edit_distance(word, given_word)

        corrections[given_word] = nsmallest(config.TOP_N_SPELLING, ed_score, key=ed_score.get)

    if words_not_in_dic:
        suggestions = combine_corrections(corrections, word_list)
        return suggestions

    #return no suggestions if no spelling corrections were necessary
    return []


def edit_distance(word1, word2):
    """Dynamic programming to calculate weighted edit distance."""
# edit distance code Adapted from Winter2020-CSI4107-TolerantRetrieval slides
# cost_swap somewhat adapted from list of common 1-letter replacements
# from http://norvig.com/ngrams/count_1edit.txt
    cost_swap = {'ae': 0.1, 'ai': 0.5, 'ao': 0.5, 'au': 0.5, 'ay': 0.5,
                 'ea': 0.5, 'ei': 0.1, 'eo': 0.5, 'eu': 0.5, 'ey': 0.5,
                 'ia': 0.5, 'ie': 0.1, 'io': 0.5, 'iu': 0.5, 'iy': 0.5,
                 'oa': 0.5, 'oe': 0.5, 'oi': 0.5, 'ou': 0.5, 'oy': 0.5,
                 'ua': 0.5, 'ue': 0.5, 'ui': 0.5, 'uo': 0.5, 'uy': 0.5,
                 'ya': 0.5, 'ye': 0.5, 'yi': 0.5, 'yo': 0.5, 'yu': 0.5,
                 'rt': 0.5, 'tr': 0.5, 'ty': 0.5, 'yt': 0.5, 'sc': 0.5,
                 'cs': 0.5, 'gh': 0.5, 'hg': 0.5, 'nm': 0.5, 'mn': 0.5,
                 'td': 0.5, 'dt': 0.5, 'ct': 0.5, 'tc': 0.5, 'sz': 0.5,
                 'zs': 0.5}
    word1 = punctuation_remover(remove_accents(word1.replace("’", "").replace("*", "")))
    word2 = punctuation_remover(remove_accents(word2.replace("’", "").replace("*", "")))
    len_word1 = len(word1)
    len_word2 = len(word2)
    array_dist = numpy.zeros((len_word2+1, len_word1+1), dtype='int32')
    # Initialization
    for i in range(len_word2+1):
        array_dist[i, 0] = i
    for j in range(len_word1+1):
        array_dist[0, j] = j
    # Reccurrence
    for i in range(1, len_word2+1):
        for j in range(1, len_word1+1):
            if word1[j-1] == word2[i-1]:
                add_fact = 0
            else:
                #convert characters to numbers
                #char_word1 = ord(word1[j-1]) - 97
                #char_word2 = ord(word2[i-1]) - 97
                add_fact = cost_swap.get(word1[j-1]+word2[i-1], 1)
            array_dist[i, j] = min(array_dist[i-1, j] + 1,
                                   array_dist[i, j-1] + 1,
                                   array_dist[i-1, j-1] + add_fact)
    return array_dist[len_word2, len_word1]

def get_spelling_dictionary(corpus):
    """Wrapper to avoid multiple dictionary reads from csv."""
    global SPELLING_CORPUS
    global SPELLING_DICT
    if SPELLING_DICT and corpus == SPELLING_CORPUS:
        return SPELLING_DICT
    SPELLING_CORPUS = corpus
    SPELLING_DICT = read_spelling_from_csv(corpus)
    return SPELLING_DICT


def read_spelling_from_csv(corpus):
    """Read in words and their frequencies from csv."""
    #spelling suggestions after lemmatizing or stemming will confuse the user
    filename = config.CORPUS[corpus]['spelling_file']
    spelling_dict = dict()
    with open(filename, 'r') as data_file:
        reader = csv.DictReader(data_file)
        for row in reader:
            spelling_dict[row['word']] = row['frequency']
    return spelling_dict

def make_first_letter_dict(spelling_dict):
    """Makes a dictionary based on the first letter of the word
        used for heuristic to reduce number of words to compare to"""
#From https://stackoverflow.com/a/47298774
    result = collections.defaultdict(list)
    for word in spelling_dict:
        result[word[0]].append(word)
    return result

#From https://stackoverflow.com/a/517974
def remove_accents(input_str):
    """Remove accents from characters"""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def list_words_not_in_dictionary(input_words, spelling_dict):
    """Returns list of words not in dictionary."""
    not_in_dict = []
    for word in input_words:
        if word not in spelling_dict and word not in ["AND", "OR", "AND_NOT", "(", ")"]:
            not_in_dict.append(word)
    return not_in_dict

def combine_corrections(corrections_dict, word_list):
    """Combine suggested corrections with words from list that
       appear in the spelling dictionary."""
    combinations = []

    for i in range(config.TOP_N_SPELLING):
        combination = []
        for word in word_list:
            if word in corrections_dict and corrections_dict[word]:
                index = min(i, max(len(corrections_dict[word]) - 1, 0))
                replaced = corrections_dict[word][index]
            else:
                replaced = word
            combination.append(replaced)
        combinations.append(combination)
    #remove dups code from https://stackoverflow.com/a/2213935
    dedup = [combinations[i] for i in range(len(combinations)) \
            if i == 0 or combinations[i] != combinations[i-1]]
    return dedup

def create_cost_dict():
    """Transform common 1-letter replacements into a cost dictionary"""
#List of common 1-letter replacements adapted from http://norvig.com/ngrams/count_1edit.txt
#Not in use right now
    count_1edit = [
        ('e', 'i', 917),
        ('a', 'e', 856),
        ('i', 'e', 771),
        ('e', 'a', 749),
        ('a', 'i', 559),
        ('s', 'c', 383),
        ('a', 'o', 353),
        ('o', 'a', 352),
        ('i', 'a', 313),
        ('e', 'o', 295),
        ('n', 'm', 230),
        ('o', 'e', 216),
        ('c', 's', 209),
        ('o', 'u', 171),
        ('u', 'e', 162),
        ('e', 'u', 160),
        ('e', 'y', 154),
        ('i', 'y', 142),
        ('m', 'n', 140),
        ('u', 'i', 133),
        ('u', 'o', 130),
        ('u', 'a', 126),
        ('y', 'i', 125),
        ('a', 'u', 123),
        ('i', 'u', 119),
        ('d', 't', 106),
        ('i', 'o', 101),
        ('o', 'i', 99),
        ('t', 'd', 87),
        ('c', 't', 65),
        ('t', 'c', 64),
        ('s', 'z', 61),
        ('s', 't', 60),
        ('c', 'g', 58),
        ('k', 'c', 53),
        ('w', 'u', 52),
        ('z', 's', 49),
        ('y', 'e', 49),
        ('p', 'b', 46),
        ('r', 'l', 45),
        ('u', 'w', 44),
        ('b', 'd', 41),
        ('v', 'f', 40),
        ('f', 'v', 39),
        ('t', 's', 38),
        ('d', 'b', 37),
        ('e', 't', 35),
        ('l', 't', 34),
        ('k', 'h', 32),
        ('b', 'p', 31),
        ('g', 'j', 30),
        ('g', 'c', 29),
        ('c', 'k', 28),
        ('r', 'e', 27),
        ('r', 'u', 26),
        ('n', 'd', 26),
        ('t', 'h', 25),
        ('r', 'n', 25),
        ('g', 'd', 24),
        ('E', 'e', 24),
        ('s', 'd', 23),
        ('n', 'r', 23),
        ('k', 't', 23),
        ('e', 's', 23),
        ('q', 'c', 22),
        ('d', 'g', 22),
        ('t', 'e', 21),
        ('l', 'r', 21),
        ('a', 'y', 21),
        ('n', 't', 20),
        ('l', 'i', 19),
        ('t', 'l', 18),
        ('d', 'e', 18),
        ('h', 'n', 17),
        ('a', 'l', 17),
        ('l', 'd', 16),
        ('l', 'b', 16),
        ('i', 't', 16),
        ('d', 'n', 16),
        ('c', 'x', 16),
        ('a', 't', 16),
        ('P', 'p', 16),
        ('x', 'c', 15),
        ('t', 'p', 15),
        ('t', 'i', 15),
        ('r', 'i', 15),
        ('r', 'd', 15),
        ('r', 'a', 15),
        ('n', 'l', 15),
        ('i', 'h', 15),
        ('h', 'e', 15),
        ('g', 't', 15),
        ('e', 'n', 15),
        ('a', 'r', 15),
        ('s', 'x', 14),
        ('r', 's', 14),
        ('r', 'f', 14),
        ('n', 's', 14),
        ('h', 't', 14),
        ('h', 'i', 14),
        ('s', 'r', 13),
        ('s', 'a', 13),
        ('r', 't', 13),
        ('n', 'u', 13),
        ('k', 'g', 13),
        ('e', 'd', 13),
        ('a', 'd', 13),
        ('D', 'd', 13),
        ('u', 'r', 12),
        ('t', 'n', 12),
        ('t', 'k', 12),
        ('s', 'e', 12),
        ('q', 'g', 12),
        ('p', 'f', 12),
        ('l', 'e', 12),
        ('j', 'g', 12),
        ('h', 'u', 12),
        ('e', 'r', 12),
        ('e', 'h', 12),
        ('c', 'a', 12),
        ('t', 'r', 11),
        ('r', 'p', 11),
        ('r', 'm', 11),
        ('l', 'w', 11),
        ('i', 'l', 11),
        ('g', 'k', 11),
        ('e', 'c', 11),
        ('e', 'b', 11),
        ('d', 'r', 11),
        ('c', 'q', 11),
        ('c', 'p', 11),
        ('y', 'u', 10),
        ('y', 'o', 10),
        ('w', 'r', 10),
        ('u', 'y', 10),
        ('u', 's', 10),
        ('u', 'n', 10),
        ('u', 'l', 10),
        ('p', 't', 10),
        ('g', 'e', 10),
        ('w', 'h', 9),
        ('s', 'n', 9),
        ('r', 'w', 9),
        ('n', 'g', 9),
        ('l', 'u', 9),
        ('l', 'n', 9),
        ('k', 'a', 9),
        ('g', 'q', 9),
        ('c', 'i', 9),
        ('b', 'v', 9),
        ('a', 's', 9),
        ('a', 'c', 9),
        ('R', 'r', 9),
        ('B', 'b', 9),
        ('A', 'E', 9),
        ('x', 's', 8),
        ('w', 'e', 8),
        ('v', 'b', 8),
        ('t', 'a', 8),
        ('p', 'm', 8),
        ('p', 'c', 8),
        ('o', 't', 8),
        ('n', 'i', 8),
        ('n', 'a', 8),
        ('c', 'n', 8),
        ('c', 'l', 8),
        ('c', 'C', 8),
        ('S', 's', 8),
        ('C', 'c', 8),
        ('y', 's', 7),
        ('t', 'f', 7),
        ('s', 'l', 7),
        ('s', 'f', 7),
        ('o', 'y', 7),
        ('h', 'p', 7),
        ('g', 'x', 7),
        ('f', 'r', 7),
        ('e', 'g', 7),
        ('d', 's', 7),
        ('d', 'j', 7),
        ('d', 'c', 7),
        ('d', 'a', 7),
        ('a', 'n', 7),
        ('G', 'g', 7),
        ('w', 'v', 6),
        ('t', 'y', 6),
        ('t', 'u', 6),
        ('t', 'g', 6),
        ('s', 'i', 6),
        ('r', 'y', 6),
        ('r', 'c', 6),
        ('p', 'r', 6),
        ('m', 't', 6),
        ('m', 'd', 6),
        ('l', 'a', 6),
        ('k', 'u', 6),
        ('h', 's', 6),
        ('h', 'r', 6),
        ('h', 'o', 6),
        ('h', 'k', 6),
        ('g', 'u', 6),
        ('f', 'l', 6),
        ('e', 'w', 6),
        ('z', 'x', 5),
        ('z', 'c', 5),
        ('y', 't', 5),
        ('w', 'o', 5),
        ('t', 'm', 5),
        ('s', 'y', 5),
        ('s', 'u', 5),
        ('s', 'p', 5),
        ('r', 'g', 5),
        ('r', 'b', 5),
        ('n', 'c', 5),
        ('m', 'p', 5),
        ('m', 'b', 5),
        ('l', 'y', 5),
        ('l', 'm', 5),
        ('g', 'm', 5),
        ('f', 'g', 5),
        ('e', 'l', 5),
        ('d', 'v', 5),
        ('d', 'u', 5),
        ('c', 'h', 5),
        ('b', 'm', 5),
        ('I', 'i', 5),
        ('y', 'n', 4),
        ('w', 's', 4),
        ('v', 't', 4),
        ('v', 'n', 4),
        ('u', 't', 4),
        ('t', 'b', 4),
        ('s', 'w', 4),
        ('s', 'S', 4),
        ('r', 'x', 4),
        ('r', 'h', 4),
        ('o', 'l', 4),
        ('n', 'w', 4),
        ('n', 'b', 4),
        ('m', 'x', 4),
        ('k', 'd', 4),
        ('j', 'd', 4),
        ('i', 'w', 4),
        ('i', 'r', 4),
        ('i', 'n', 4),
        ('g', 's', 4),
        ('f', 't', 4),
        ('f', 'p', 4),
        ('f', 'n', 4),
        ('f', 'c', 4),
        ('e', 'm', 4),
        ('d', 'w', 4),
        ('d', 'l', 4),
        ('a', 'A', 4),
        ('y', 'w', 3),
        ('y', 'r', 3),
        ('y', 'c', 3),
        ('v', 'x', 3),
        ('v', 'w', 3),
        ('v', 'i', 3),
        ('v', 'c', 3),
        ('u', 'm', 3),
        ('t', 'w', 3),
        ('s', 'm', 3),
        ('s', 'g', 3),
        ('p', 's', 3),
        ('p', 'h', 3),
        ('o', 'w', 3),
        ('o', 'r', 3),
        ('o', 'h', 3),
        ('n', 'y', 3),
        ('n', 'f', 3),
        ('m', 'w', 3),
        ('m', 's', 3),
        ('m', 'r', 3),
        ('m', 'M', 3),
        ('l', 's', 3),
        ('l', 'k', 3),
        ('l', 'f', 3),
        ('l', 'c', 3),
        ('k', 'p', 3),
        ('k', 'l', 3),
        ('h', 'c', 3),
        ('g', 'r', 3),
        ('f', 's', 3),
        ('f', 'e', 3),
        ('f', 'F', 3),
        ('e', 'p', 3),
        ('e', 'k', 3),
        ('d', 'p', 3),
        ('d', 'm', 3),
        ('d', 'k', 3),
        ('d', 'i', 3),
        ('c', 'u', 3),
        ('c', 'r', 3),
        ('c', 'f', 3),
        ('c', 'd', 3),
        ('b', 'r', 3),
        ('a', 'w', 3),
        ('a', 'h', 3),
        ('M', 'm', 3),
        ('z', 'g', 2),
        ('y', 'v', 2),
        ('y', 'l', 2),
        ('y', 'h', 2),
        ('y', 'g', 2),
        ('y', 'a', 2),
        ('x', 'z', 2),
        ('x', 't', 2),
        ('x', 'n', 2),
        ('w', 'm', 2),
        ('w', 'l', 2),
        ('w', 'k', 2),
        ('w', 'a', 2),
        ('v', 'l', 2),
        ('v', 'g', 2),
        ('u', 'h', 2),
        ('t', 'j', 2),
        ('t', 'T', 2),
        ('s', 'h', 2),
        ('r', 'v', 2),
        ('r', 'R', 2),
        ('q', 't', 2),
        ('q', 'a', 2),
        ('p', 'a', 2),
        ('p', 'P', 2),
        ('o', 'g', 2),
        ('n', 'o', 2),
        ('n', 'e', 2),
        ('m', 'f', 2),
        ('m', 'e', 2),
        ('l', 'v', 2),
        ('l', 'p', 2),
        ('l', 'j', 2),
        ('l', 'g', 2),
        ('k', 'y', 2),
        ('k', 'x', 2),
        ('k', 's', 2),
        ('k', 'o', 2),
        ('j', 'h', 2),
        ('j', 'J', 2),
        ('i', 's', 2),
        ('i', 'd', 2),
        ('i', 'E', 2),
        ('h', 'l', 2),
        ('h', 'f', 2),
        ('g', 'y', 2),
        ('f', 'd', 2),
        ('f', 'b', 2),
        ('e', 'f', 2),
        ('d', 'y', 2),
        ('c', 'z', 2),
        ('c', 'w', 2),
        ('c', 'v', 2),
        ('c', 'e', 2),
        ('b', 't', 2),
        ('b', 'n', 2),
        ('b', 'f', 2),
        ('b', 'B', 2),
        ('a', 'p', 2),
        ('a', 'm', 2),
        ('S', 'Z', 2),
        ('F', 'f', 2),
        ('A', 'a', 2),
        ('-', 'y', 2),
        ('z', 't', 1),
        ('z', 'l', 1),
        ('z', 'd', 1),
        ('y', 'm', 1),
        ('y', 'j', 1),
        ('y', 'd', 1),
        ('x', 'y', 1),
        ('x', 'm', 1),
        ('x', 'l', 1),
        ('w', 'y', 1),
        ('w', 't', 1),
        ('w', 'i', 1),
        ('w', 'f', 1),
        ('w', 'd', 1),
        ('w', 'b', 1),
        ('w', 'W', 1),
        ('w', '-', 1),
        ('v', 'z', 1),
        ('v', 'y', 1),
        ('v', 'u', 1),
        ('v', 'p', 1),
        ('v', 'm', 1),
        ('v', 'd', 1),
        ('v', 'V', 1),
        ('u', 'v', 1),
        ('u', 'j', 1),
        ('u', 'g', 1),
        ('u', 'f', 1),
        ('u', 'c', 1),
        ('t', 'x', 1),
        ('t', 'q', 1),
        ('s', 'v', 1),
        ('s', 'o', 1),
        ('r', 'o', 1),
        ('r', 'k', 1),
        ('r', 'j', 1),
        ('p', 'y', 1),
        ('p', 'o', 1),
        ('p', 'l', 1),
        ('p', 'i', 1),
        ('p', 'g', 1),
        ('p', 'd', 1),
        ('o', 's', 1),
        ('o', 'n', 1),
        ('o', 'd', 1),
        ('o', 'O', 1),
        ('n', 'z', 1),
        ('n', 'x', 1),
        ('n', 'v', 1),
        ('n', 'p', 1),
        ('n', 'h', 1),
        ('n', 'N', 1),
        ('m', 'v', 1),
        ('m', 'u', 1),
        ('m', '.', 1),
        ('l', 'o', 1),
        ('l', 'h', 1),
        ('j', 'v', 1),
        ('j', 't', 1),
        ('i', 'x', 1),
        ('i', 'm', 1),
        ('i', 'j', 1),
        ('i', 'f', 1),
        ('i', 'I', 1),
        ('h', 'y', 1),
        ('h', 'w', 1),
        ('h', 'm', 1),
        ('h', 'j', 1),
        ('h', 'a', 1),
        ('h', 'H', 1),
        ('g', 'z', 1),
        ('g', 'p', 1),
        ('g', 'o', 1),
        ('g', 'l', 1),
        ('g', 'h', 1),
        ('g', 'f', 1),
        ('g', 'a', 1),
        ('g', 'G', 1),
        ('f', 'w', 1),
        ('f', 'k', 1),
        ('f', 'i', 1),
        ('f', 'h', 1),
        ('d', 'z', 1),
        ('d', 'h', 1),
        ('d', 'f', 1),
        ('d', 'D', 1),
        ('c', 'o', 1),
        ('c', 'b', 1),
        ('b', 'w', 1),
        ('b', 'o', 1),
        ('b', 'l', 1),
        ('b', 'g', 1),
        ('b', 'e', 1),
        ('b', 'a', 1),
        ('a', 'f', 1),
        ('a', 'b', 1),
        ('a', 'I', 1),
        ('V', 'v', 1),
        ('U', 'u', 1),
        ('S', 'C', 1),
        ('R', 'c', 1),
        ('O', 'o', 1),
        ('L', 'l', 1),
        ('K', 'k', 1),
        ('K', 'c', 1),
        ('J', 'g', 1),
        ('I', 'a', 1),
        ('C', 'g', 1),
        ('B', 'M', 1),
        ('-', 's', 1),
        ('-', 'p', 1),
        ('-', 'l', 1),
        ('-', 'e', 1)]
    cost_dict = dict()
    for entry in count_1edit:
        letter_from = entry[0]
        letter_to = entry[1]
        cost_dict[letter_from+letter_to] = 1/entry[2]
    return cost_dict
