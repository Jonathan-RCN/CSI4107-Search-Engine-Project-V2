import ast
from config import UOTTAWA, REUTERS
import config
# import Reteurs.local_query_expansion_rocchio as LQE


def initialize_dicts():
    config.RELEVANCE_DICT_UOTTAWA = dict()
    config.RELEVANCE_DICT_REUTERS = dict()
#
# initialize_dicts()
# print(RELEVANCE_DICT_UOTTAWA)


def update_relevance(query_key, doc_id, corpus):

    if corpus == UOTTAWA:
        current_dict = config.RELEVANCE_DICT_UOTTAWA
    else:
        current_dict = config.RELEVANCE_DICT_REUTERS

    if current_dict.get(query_key):
        relevance_list=current_dict[query_key]
        flag = 0
        if doc_id in relevance_list[0]:
            relevance_list[0].remove(doc_id)
            relevance_list[1].append(doc_id)
        elif doc_id in relevance_list[1]:
            relevance_list[1].remove(doc_id)

            if relevance_list[0]==[] and relevance_list[1]==[]:
                del current_dict[query_key]
                flag=1

        else:
            relevance_list[0].append(doc_id)

        if flag==0:
            current_dict[query_key]=relevance_list
    else:
        current_dict[query_key]= [[doc_id], []]

    # print(current_dict)
    # LQE.test()




def get_relevance(query_key, doc_id, corpus):

    if corpus == UOTTAWA:
        current_dict = config.RELEVANCE_DICT_UOTTAWA
    else:
        current_dict = config.RELEVANCE_DICT_REUTERS
    if current_dict.get(query_key):
        if doc_id in current_dict[query_key][0]:
            return 'Relevant'
        elif doc_id in current_dict[query_key][1]:
            return 'Not Relevant'
        else:
            return 'Error'

    else:
        return "Neutral"



def retreive_relevance_as_list(query_key, corpus):

    if corpus == UOTTAWA:
        current_dict = config.RELEVANCE_DICT_UOTTAWA
    else:
        current_dict = config.RELEVANCE_DICT_REUTERS
    return current_dict.get(query_key)


# def encapsulate():
#     update_relevace('key_test',1,config.UOTTAWA)
#
#     #print(RELEVANCE_DICT_REUTERS)
#     update_relevace('key_test',1,config.REUTERS)
#     #print(RELEVANCE_DICT_REUTERS)
#     update_relevace('key_test',2,config.REUTERS)
#     #print(RELEVANCE_DICT_REUTERS)
#     update_relevace('key_test',1,config.REUTERS)
#     #print(RELEVANCE_DICT_REUTERS)
#     update_relevace('key_test',1,config.REUTERS)
#     #print(RELEVANCE_DICT_REUTERS)
#     update_relevace('key_test',1,config.REUTERS)
#     #print(RELEVANCE_DICT_REUTERS)



