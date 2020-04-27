from nltk.corpus import wordnet
from nltk.corpus import wordnet as wn
import random
import config
synonyms = []
antonyms = []

class ExpandedQuery:
    """ Sourced from Tiffany since it is interacting with the GUI"""
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
    if search_type == 'Boolean' and (len(input_query.split()) <= (2*config.QEM_MAX_QUERY_WORD_LEN_FOR_EXP-1)):
        #allow for boolean terms AND, OR, AND_NOT between query words
        return qem_bool_query(input_query)
    #input query too long, return input as expanded
    return ExpandedQuery(input_query, input_query, [])


def qem_vsm_query(query):
    """limitarions if there is more than one word to expanded, and a word does not return any synonyms the expansion space is not
    redistibuted between the other words"""
    query_ind_words=query.split()

    expansion_word_list_list = qem_vsm_bool_word_expandor(query_ind_words)

    expanded_query = ''
    suggestions_list = []
    #print(expansion_word_list_list)
    for expansion_set in expansion_word_list_list:
        base_word=expansion_set[0]
        expanded_query = f'{expanded_query} {base_word}'
        for secondary_word in expansion_set[1]:
            expanded_query=f'{expanded_query} {secondary_word}'
            suggestions_list.append(f'{base_word} {secondary_word}')
    expanded_query=expanded_query.strip()
    print(expanded_query)
    print(suggestions_list)
    return ExpandedQuery(query, expanded_query, suggestions_list)

def qem_bool_query(query):
    """limitarions if there is more than one word to expanded, and a word does not return any synonyms the expansion space is not
        redistibuted between the other words

        Does not expand wildcards prior to expansion// however probably not necesarry as the WC expansion will deal with similar terms
        """


    bool_terms = ["AND", "OR", "AND_NOT", "(", ")"]
    bool_terms_2=["AND", "OR", "AND_NOT"]
    # if query[0]!='(' or query[len(query)-1]!=')': # // assumption if have opening ( also has closing )
    #     query=f'({query})'
    query = query.replace('(', '( ').replace(')', ' )')
    bool_word_list=[]
    query_ind_words=[]
    for word in query.split():
        # since wildcard is not expanded -> cannot be processed by WN
        if word in bool_terms:# or word.find('*')>0:
            bool_word_list.append(word)
        else:
            query_ind_words.append(word)



    # print(bool_word_list)
    # print(query_ind_words)
    expansion_word_list_list = qem_vsm_bool_word_expandor(query_ind_words)
    # The expandor returned no words
    if expansion_word_list_list == []:
        return ExpandedQuery(query, query, [])

    print (expansion_word_list_list)

    suggestion_list=[]
    or_expansion_list=[]
    for expansion_set in expansion_word_list_list:
        base_word=expansion_set[0]
        or_expansion = base_word
        for secondary_word in expansion_set[1]:
            or_expansion= f'{or_expansion} OR {secondary_word}'
            suggestion_list.append(f'({base_word} OR {secondary_word})')
        if or_expansion!=base_word:
            or_expansion=f'({or_expansion})'
        or_expansion_list.append(or_expansion)
    print(or_expansion_list)

    expanded_query_2 = ''
    quere_split_2 = query.split()
    # print(quere_split_2)
    or_exp_index_2 = 0
    for words in quere_split_2:
        # print(expanded_query_2)
        if words in bool_terms:
            expanded_query_2 = f'{expanded_query_2} {words}'
        else:
            expanded_query_2 = f'{expanded_query_2} {or_expansion_list[or_exp_index_2]}'
            or_exp_index_2 += 1

    expanded_query_2 = expanded_query_2.replace('( ', '(').replace('  )', ')').replace(' )', ')')
    # print(expanded_query_2)
    # print (suggestion_list)

    return ExpandedQuery(query, expanded_query_2, suggestion_list)



    # expanded_query=''
    #
    # # expanded_query=bool_word_list[0]
    # or_exp_list_len=len(or_expansion_list)
    # bool_list_len=len(bool_word_list)
    # if bool_word_list[0] == '(':
    #     expanded_query = bool_word_list[0]
    #     bool_word_list[0]='/'
    #     bool_index = 1
    # else:
    #     expanded_query = ''
    #     bool_index = 0
    # or_exp_index = 0
    # #print('///////////////////////////')
    # while or_exp_index <or_exp_list_len and bool_index < bool_list_len:
    #     # print(f'Bool index; {bool_index}')
    #     # print(or_expansion_list[or_exp_index])
    #     # print(bool_word_list[bool_index])
    #
    #     if bool_word_list[bool_index -1] ==')':
    #         expanded_query = f'{expanded_query}{bool_word_list[bool_index]} {or_expansion_list[or_exp_index]} '
    #         or_exp_index += 1
    #         bool_index += 1
    #
    #     elif bool_word_list[bool_index] in bool_terms_2:
    #         #print(1)
    #         expanded_query = f'{expanded_query}{or_expansion_list[or_exp_index]} {bool_word_list[bool_index]} '
    #         or_exp_index += 1
    #         bool_index += 1
    #     elif bool_word_list[bool_index -1] in bool_terms_2:
    #         #print(2)
    #         expanded_query = f'{expanded_query}{or_expansion_list[or_exp_index]} {bool_word_list[bool_index]} '
    #         or_exp_index += 1
    #         bool_index += 1
    #
    #     else:
    #         #print(3)
    #         expanded_query = f'{expanded_query}{bool_word_list[bool_index]} '
    #         bool_index += 1
    #     #print('------------')
    #    #print(expanded_query)
    #     #print('==============================')
    #
    #
    #
    #
    # while bool_index<bool_list_len:
    #     expanded_query = f'{expanded_query}{bool_word_list[bool_index]} '
    #     bool_index += 1
    # while or_exp_index <or_exp_list_len:
    #     expanded_query = f'{expanded_query}{or_expansion_list[or_exp_index]}'
    #     or_exp_index += 1
    #     bool_index += 1





def qem_vsm_bool_word_expandor(ind_word_list):
    # distributing expansion space between all origional words
    list_length=len(ind_word_list)
    wild_card_counter=0
    # wildcards don't get expanded therefore they should not impact how many synonyms the other words get
    for element in ind_word_list:
        if element.find('*')>0:
            wild_card_counter+=1
    functionnal_list_length= list_length - wild_card_counter
    if functionnal_list_length == 0:
        return []
    num_syns_per_word = int(config.QEM_MAX_TOTAL_WORD_COUNT / functionnal_list_length)
    # need to account for inital word in the total count
    num_syns_per_word -= 1
    # if expansion space/word is 0 change to one s.t. each word can suggest at least another alternative
    if num_syns_per_word == 0:
        num_syns_per_word = 1
    # print(num_syns_per_word)

    expansion_word_list_list = []

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
    if sum(word_type_synonym_count)==0:
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
    if word_type_count_1>word_type_count_2:
        word_type_index=word_type_synonym_count.index(word_type_count_1)
    else:
        word_type_index = word_type_synonym_count.index(word_type_count_2)
    # determining the part of speech that will be actually used
    if word_type_index == 0:
        word_type= wn.NOUN
    elif word_type_index ==1:
        word_type = wn.VERB
    elif word_type_index ==2:
        word_type = wn.ADJ
    elif word_type_index ==3:
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

    :param query:
    :param word_type:
    :return:
    """
    tier_1_syn=[]
    tier_2_syn=[]

    # getting all the synset for the given query/word type
    for syn in wn.synsets(query, pos=word_type):
        syn_string=str(syn)
        # determining if the original query is in the produced synset
        if syn_string.find(f"'{query}.") >0:
            tier_1_syn.append(syn)
        else:
            tier_2_syn.append(syn)
    tier_1_lemmas=[]
    tier_2_lemmas=[]
    tier_3_lemmas = []
    # print(tier_1_syn)
    # print(tier_2_syn)
    #getting lemmas of the synset
    for syns in tier_1_syn:
        for l in syns.lemmas():
            tier_1_lemmas.append(l.name().lower())
    for syns in tier_2_syn:
        flag=0
        for l in syns.lemmas():
            # putting the first lemma for the given synset into its own list
            if flag==0:
                tier_2_lemmas.append(l.name().lower())
                flag=1
            else:
                tier_3_lemmas.append(l.name().lower())

    # removing the original query from synonym list
    tier_1_lemmas=[syn for syn in tier_1_lemmas if syn != query]
    tier_2_lemmas=[syn for syn in tier_2_lemmas if syn != query]
    tier_3_lemmas = [syn for syn in tier_3_lemmas if syn != query]
    return  tier_1_lemmas, tier_2_lemmas, tier_3_lemmas

def word_selector(primary_words, secondary_words, tertiary_words, expansion_limit):
    """
    Selecting the words to be used in the query expansion.

    If number of primary words is less than the expansion limit, include all of those words. Then select at random from
    secondary (then tertiary words if all secondary words have been used) until the expansion limit has been meet.

    If the number of primary words is greater than expansion limit, selected primary words at random until expansion limit
    is reached.

    :param primary_words:
    :param secondary_words:
    :param tertiary_words:
    :param expansion_limit:
    :return:
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


#qem_bool_query('(oil AND cat) OR dog')

# qem_vsm_query("U.S. corn market")
#
#
#
#
#
# print(qem_word_selector_wrapper('Canada', 5))
