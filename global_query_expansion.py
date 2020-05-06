"""
Title: Query Expansion Module

Project: CSI4107 Project
Version: Final System
Component: Module 3

Created: 26 Apr 2020

Author: Jonathan Boerger
Status: Completed

Description: This module provides explicit query expansion through the use of the word net database and interfaces
with the GUI (module 7) to display these expansions.
In addition to query expansion, it also determines query suggestions which are one synonym subsets of the entire
query expansion.

Detailed description can be found bellow


Limitation:
    Synonym relvance is a best-guess and relies on randomness.

    Query word expansion slots are fixed. I.e. if a word uses less than their alocated expansion slots they are not
    redistributed to the other query words.

General references:
    -https://pythonprogramming.net/wordnet-nltk-tutorial/
    -https://www.nltk.org/howto/wordnet.html


    As detailled in the project report, I was unable to implement module 7. Therefore, I have adapted Tiffany Maynard
    GUI for her version of this project to work with this module. As a result, some methods are structured similarily
    to allow for intergration.
"""
# detailed description
"""
Extended Description

Query expansion works for both boolean and VSM queries

This module only applies synonyms (does not include hypernyms).

Expansion is only perform if the initial query is less than 4 words long. It is assumed that if the query is more than
four words, the user is being specific enough that additional expansion is not required.

Wildcard words are not considered for expansion since they will be expanded through the wildcard handeler.

Additionally, this query expander only suggest words from  a single part of speech/ gramatical caterogy
(for ex noun, verb, adjective, adverb).

As such only certain words are available for expansion:
    -If a word falls under 3 or more gramatical caterogy it will not be considered for expansion as there are too many
    possible usage of the base word. Therfore, it is not feasible to infer which category the orional usage fall under.

    -If the words fall under two categories, a configurable definition distribution ratio is used to determine if the
    expansion should procced. That is to say, for the expansion to continue there needs to be a clear majority
    (configurable threshold) of possible word sense towards one of the gramatical categories.
    For example if a word has 5 usages as a noun but only 1 as a verb, the query expansion will continue for the noun.
    However if the word had 2 usages as a noun and 2 usages as a verb, the expansion would not continue as the gramatical
    sense of the word is ambigous.

Once the word has been ok for expansion and grmatical category selected, the module attemps to sort the synonyms into 
sudo-relevant categories. 
These categories are as follows:
    -Tier one(high): are all synonyms associated with a word sense when the synset for the query contians the query 
    as the top level word. 
    For example with dog: All synonyms of Synset('dog.n.01') would be considered a teir 1 synonym. 
    
    -Tier two (medium): When a word other than the base word appears in the synset, teir two words are the top level 
    word for that given synset. 
    For example with dog: returns Synset('cad.n.01'), therfore 'cad' would be a tier two synonym. 
    
    -Tier three (low): All the synonyms associated with the teir 2 synsets.
    Example: All the synonums of cad for Synset('cad.n.01').
    
    The obvious limation is that this is simply a rough guess at synonym relevance. More detailed models could be employed
    to not only better dived the words into the 3 tiers, but also sort within the tiers themselves. This would 
    eliminate the need to randomness in the next section. 
    
Moreover, given there is limited space to display query expansions, this module determines which synonyms should be selected
to expand the query.
In order to acheive this, the module first determines how many expansion slots each word in the query has. 
For there, each word gets it sysnonyms. If there are more tier one synonyms that expansion slots for the given word
then tier one synonyms are selected at random. 
Otherwise and all teir one synonyms as selected and remaning expansion space is made up by randomly selecting tier 2 
and tier 3 synonyms (if there is still expansion space after all tier two synonyms have been selected).  

Currently, there is a limitation, that if a word in the query is not expandable, its expansion slots are not 
redistributed to the other query words (this does not apply to wildcard search terms)

Lastly, the expanded queries are intergrated into the original query and sent back to the GUI.
"""

from nltk.corpus import wordnet as wn
import random
import config

synonyms = []
antonyms = []


class ExpandedQuery:
    """ Sourced from Tiffany Maynard since it is interacting with the GUI"""
    """Expanded query holds all the info for providing suggestions"""
    initial_query: str
    expanded_query: str
    suggestions: []

    def __init__(self, initial_query, expanded_query, suggestions):
        """Initialize expanded query"""
        self.initial_query = initial_query
        self.expanded_query = expanded_query
        self.suggestions = suggestions


def qem_word_selector_wrapper(query, expansion_limit):
    """
    Wrapper method that emplements the qeury expansion strategy employed by this module.
    Determines if a query is eligible for expansion and if so what gramatical category will be considerd.
    """
    pass_fail, word_type = determine_query_expansion_eligibility(query)
    # print(pass_fail, word_type)
    if pass_fail == False:
        return []
    primary_words, secondary_words, tertiary_words = sort_syn_lemmas(query, word_type)
    # print(primary_words)
    # print(secondary_words)
    # print(tertiary_words)
    expansion_words = word_selector(primary_words, secondary_words, tertiary_words, expansion_limit)
    # print(expansion_words)
    return expansion_words


def create_global_expanded_query(input_query, search_type):
    """ Sourced from Tiffany since it is interacting with the GUI"""
    """Return an expanded VSM or boolean query given a starting query"""
    if search_type == 'VSM' and (len(input_query.split()) <= config.QEM_MAX_QUERY_WORD_LEN_FOR_EXP):
        return qem_vsm_query(input_query)
    if search_type == 'Boolean' and (len(input_query.split()) <= (2 * config.QEM_MAX_QUERY_WORD_LEN_FOR_EXP - 1)):
        # allow for boolean terms AND, OR, AND_NOT between query words
        return qem_bool_query(input_query)
    # input query too long, return input as expanded
    return ExpandedQuery(input_query, input_query, [])


def qem_vsm_query(query):
    """
    Takes and expands a vsm query
    """
    query_ind_words = query.split()

    expansion_word_list_list = qem_vsm_bool_word_expandor(query_ind_words)

    expanded_query = ''
    suggestions_list = []
    # print(expansion_word_list_list)
    for expansion_set in expansion_word_list_list:
        base_word = expansion_set[0]
        # adding the synonyms after the base word in the query
        expanded_query = f'{expanded_query} {base_word}'
        for secondary_word in expansion_set[1]:
            expanded_query = f'{expanded_query} {secondary_word}'
            # capturing possible query suggestions from the base word and each of its selected synonyms
            suggestions_list.append(f'{base_word} {secondary_word}')
    expanded_query = expanded_query.strip()
    print(expanded_query)
    print(suggestions_list)
    return ExpandedQuery(query, expanded_query, suggestions_list)


def qem_bool_query(query):
    """
    Takes and returns a boolean formated expanded query where sysnonynms are seperated by OR

    Does not expand or process wildcards since they are handled via the wildcard module
    """

    bool_terms = ["AND", "OR", "AND_NOT", "(", ")"]
    query = query.replace('(', '( ').replace(')', ' )')
    bool_word_list = []
    query_ind_words = []
    for word in query.split():
        # since wildcard is not expanded -> cannot be processed by WN
        if word in bool_terms:
            bool_word_list.append(word)
        else:
            query_ind_words.append(word)

    # getting the actual synonyms
    expansion_word_list_list = qem_vsm_bool_word_expandor(query_ind_words)
    # The expandor returned no words
    if expansion_word_list_list == []:
        return ExpandedQuery(query, query, [])

    print(expansion_word_list_list)

    suggestion_list = []
    or_expansion_list = []
    for expansion_set in expansion_word_list_list:
        base_word = expansion_set[0]
        or_expansion = base_word
        for secondary_word in expansion_set[1]:
            # creating OR bool term for all synonms of base word
            or_expansion = f'{or_expansion} OR {secondary_word}'
            # creating suggestion pairs from base word with all of its selected synonyms
            suggestion_list.append(f'({base_word} OR {secondary_word})')
        if or_expansion != base_word:
            or_expansion = f'({or_expansion})'
        or_expansion_list.append(or_expansion)
    print(or_expansion_list)

    # intergrateing synonyms into base boolean query
    expanded_query_2 = ''
    quere_split_2 = query.split()
    or_exp_index_2 = 0
    for words in quere_split_2:
        # print(expanded_query_2)
        if words in bool_terms:
            expanded_query_2 = f'{expanded_query_2} {words}'
        else:
            expanded_query_2 = f'{expanded_query_2} {or_expansion_list[or_exp_index_2]}'
            or_exp_index_2 += 1

    expanded_query_2 = expanded_query_2.replace('( ', '(').replace('  )', ')').replace(' )', ')')

    return ExpandedQuery(query, expanded_query_2, suggestion_list)


def qem_vsm_bool_word_expandor(ind_word_list):
    """
     Takes all the word in a query, determine how many expansion slots for each word and get the synonyms for that word
     Does not expand or process wildcards since they are handled via the wildcard module
    """
    # distributing expansion space between all origional words
    list_length = len(ind_word_list)
    wild_card_counter = 0
    # wildcards don't get expanded therefore they should not impact how many synonyms the other words get
    for element in ind_word_list:
        if element.find('*') > 0:
            wild_card_counter += 1
    functionnal_list_length = list_length - wild_card_counter

    # if no words to expand
    if functionnal_list_length == 0:
        return []

    # determining expansion slots per individual word
    num_syns_per_word = int(config.QEM_MAX_TOTAL_WORD_COUNT / functionnal_list_length)
    # need to account for inital word in the total count
    num_syns_per_word -= 1
    # if expansion space/word is 0 change to one s.t. each word can suggest at least another alternative
    if num_syns_per_word == 0:
        num_syns_per_word = 1
    # print(num_syns_per_word)

    expansion_word_list_list = []

    # getting the synonyms
    for word in ind_word_list:
        expanded_words = qem_word_selector_wrapper(word.lower(), num_syns_per_word)
        # print(expanded_words)
        expansion_word_list_list.append([word, expanded_words])
    return expansion_word_list_list


def determine_query_expansion_eligibility(query):
    """
    Determining if a word is eligible for expansion based on the word characterics.

    Not eligible if the word has definitions for more than two word sense (part of speech tag) from
    noun, verb, adjective, adverb.

    Furthermore, not eligble if the distribution between the definitions of the two word senses is less than a defined ration.
    That is to say if for a word 6 definitions are nouns and 4 are verbs, the ratio between words is 1.5. Therefore
    if the minimum ratio was 2, this word would not be eligible.

    These rules are puy in place since they filter out words with too many possible word senses to be able to infer the intended
    word sense in the original query.

    """

    syn_set_by_word_type_list = []  # Noun, verb, adj, adv
    # getting the number of synonyms by word type
    syn_set_by_word_type_list.append(wn.synsets(query, pos=wn.NOUN))
    syn_set_by_word_type_list.append(wn.synsets(query, pos=wn.VERB))
    syn_set_by_word_type_list.append(wn.synsets(query, pos=wn.ADJ))
    syn_set_by_word_type_list.append(wn.synsets(query, pos=wn.ADV))
    word_type_count = 0
    word_type_synonym_count = []
    # determining how many part of speech tags the original query satisfies, as well as getting the number of definitions for each category
    for word_type in syn_set_by_word_type_list:
        if word_type != []:
            word_type_count += 1
            word_type_synonym_count.append(len(word_type))
        else:
            word_type_synonym_count.append(0)

    # as per the eligibility rules, since this word has more than 3 part of speech tags, it is not eligible
    if word_type_count >= 3:
        print('This word has too many potential word types to reasonably decipher the intended usage')
        return False, 'Nil'
    # if there are no synonyms stop processing the word
    if sum(word_type_synonym_count) == 0:
        return False, "Nil"

    word_type_count_1 = 0
    word_type_count_2 = 0
    for word_count in word_type_synonym_count:
        if word_count == 0:
            pass
        elif word_type_count_1 == 0:
            word_type_count_1 = word_count
        else:
            word_type_count_2 = word_count
    # determining the ratio between the two sets of part of speech definitions

    word_count_ratio = word_type_count_2 / word_type_count_1
    target_ratio = config.QEM_MIN_WORD_TYPE_DISTR_RATIO
    target_ratio_inverse = 1 / target_ratio
    # print(word_count_ratio)
    # if ratio is 0, indicates there is only 1 word.
    if word_count_ratio != 0:
        # as per the eligibility rules, ratio does not meet the required standard, the word is not eligible
        if word_count_ratio < target_ratio_inverse and word_count_ratio > target_ratio:
            print(
                'The ratio between the distribution of synonyms between the two word types is too close. Thus it is not possible to determine the intended usage')
            return False, "Nil"

    # if two types of part of speech, take type with most definitions
    if word_type_count_1 > word_type_count_2:
        word_type_index = word_type_synonym_count.index(word_type_count_1)
    else:
        word_type_index = word_type_synonym_count.index(word_type_count_2)
    # determining the part of speech that will be actually used
    if word_type_index == 0:
        word_type = wn.NOUN
    elif word_type_index == 1:
        word_type = wn.VERB
    elif word_type_index == 2:
        word_type = wn.ADJ
    elif word_type_index == 3:
        word_type = wn.ADV
    else:
        print('Error')
        return False, 'Nil'
    return True, word_type


def sort_syn_lemmas(query, word_type):
    """
    Splitting the sysnonyms of the querry into 3 categories to establish sudo relevance between synonyms associated from
    the same synsets query.

    Tier 1 lemmas are the synonyms of the querry where the synset contains the actual query
        For example 'dog': Tier one lemmas would contain the synonyms of Synset('dog.n.01') and Synset('dog.n.03')

    Tier 2 lemmas are the leading synonym of synsets that do not contain the actual query
        For example 'dog': Tier two lemmas would contain 'cad' since synsets('dog') returns Synset('cad.n.01')

    Tier 3 lemmas are the ramaning synonyms of synsets that do not contain the actual query
        For example 'dog': Tier three lemmas would contain 'bounder, blackguard,etc..' since they are they are the lemmas of Synset('cad.n.01')

    The higher the tier the higher the assumed relevance.
    """
    tier_1_syn = []
    tier_2_syn = []

    # getting all the synset for the given query/word type
    for syn in wn.synsets(query, pos=word_type):
        syn_string = str(syn)
        # determining if the original query is in the produced synset
        if syn_string.find(f"'{query}.") > 0:
            tier_1_syn.append(syn)
        else:
            tier_2_syn.append(syn)
    tier_1_lemmas = []
    tier_2_lemmas = []
    tier_3_lemmas = []
    # print(tier_1_syn)
    # print(tier_2_syn)
    # getting lemmas of the synset
    for syns in tier_1_syn:
        for l in syns.lemmas():
            tier_1_lemmas.append(l.name().lower())
    for syns in tier_2_syn:
        flag = 0
        for l in syns.lemmas():
            # putting the first lemma for the given synset into its own list
            if flag == 0:
                tier_2_lemmas.append(l.name().lower())
                flag = 1
            else:
                tier_3_lemmas.append(l.name().lower())

    # removing the original query from synonym list
    tier_1_lemmas = [syn for syn in tier_1_lemmas if syn != query]
    tier_2_lemmas = [syn for syn in tier_2_lemmas if syn != query]
    tier_3_lemmas = [syn for syn in tier_3_lemmas if syn != query]
    return tier_1_lemmas, tier_2_lemmas, tier_3_lemmas


def word_selector(primary_words, secondary_words, tertiary_words, expansion_limit):
    """
    Selecting the words to be used in the query expansion.

    If number of primary words is less than the expansion limit, include all of those words. Then select at random from
    secondary (then tertiary words if all secondary words have been used) until the expansion limit has been meet.

    If the number of primary words is greater than expansion limit, selected primary words at random until expansion limit
    is reached.
    """

    words_for_expanded_querry = []
    # all primary words fit in expansion space
    if len(primary_words) <= expansion_limit:

        for word in primary_words:
            words_for_expanded_querry.append(word)
        # select random secondary words add to expansion space given that expansion space has not reached expansion limit
        # and there are still secondary words available
        while len(words_for_expanded_querry) < expansion_limit and secondary_words != []:
            word_to_add = random.choice(secondary_words)
            words_for_expanded_querry.append(word_to_add)
            # removing word from list s.t. it is not randomly selected a second time.
            secondary_words.remove(word_to_add)

        # select random tertiary words add to expansion space given that expansion space has not reached expansion limit
        # and there are still tertiary words available
        while len(words_for_expanded_querry) < expansion_limit and tertiary_words != []:
            word_to_add = random.choice(tertiary_words)
            words_for_expanded_querry.append(word_to_add)
            tertiary_words.remove(word_to_add)

    else:
        # more primary words than available expansion space -> select randomly primary words until expansion space is full
        while len(words_for_expanded_querry) < expansion_limit and primary_words != []:
            word_to_add = random.choice(primary_words)
            words_for_expanded_querry.append(word_to_add)
            primary_words.remove(word_to_add)

    return words_for_expanded_querry
