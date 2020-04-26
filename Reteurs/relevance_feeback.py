import ast
from config import UOTTAWA, REUTERS
import config

RELEVANCE_DICT_UOTTAWA=dict()
RELEVANCE_DICT_REUTERS=dict()

def initialize_dicts():
    RELEVANCE_DICT_UOTTAWA['key_test']=[56],[100]
    RELEVANCE_DICT_REUTERS['key_test '] = [100],[56]
#
# initialize_dicts()
# print(RELEVANCE_DICT_UOTTAWA)


def update_relevance(query_key, doc_id, corpus):
    global RELEVANCE_DICT_UOTTAWA
    global RELEVANCE_DICT_REUTERS
    if corpus == UOTTAWA:
        current_dict = RELEVANCE_DICT_UOTTAWA
    else:
        current_dict = RELEVANCE_DICT_REUTERS

    if current_dict.get(query_key):
        relevance_list=current_dict[query_key]
        dict_value_list = list(relevance_list)
        flag = 0
        if doc_id in dict_value_list[0]:
            dict_value_list[0].remove(doc_id)
            dict_value_list[1].append(doc_id)
        elif doc_id in dict_value_list[1]:
            dict_value_list[1].remove(doc_id)

            if dict_value_list[0]==[] and dict_value_list[1]==[]:
                del current_dict[query_key]
                flag=1

        else:
            dict_value_list[0].append(doc_id)

        if flag==0:
            current_dict[query_key]=dict_value_list
    else:
        current_dict[query_key]= [doc_id], []

def get_relevance(query_key, doc_id, corpus):
    global RELEVANCE_DICT_UOTTAWA
    global RELEVANCE_DICT_REUTERS
    if corpus == UOTTAWA:
        current_dict = RELEVANCE_DICT_UOTTAWA
    else:
        current_dict = RELEVANCE_DICT_REUTERS
    if current_dict.get(query_key):
        if doc_id in current_dict[query_key][0]:
            return 'Relevant'
        elif doc_id in current_dict[query_key][1]:
            return 'Not Relevant'
        else:
            return 'Error'

    else:
        return "Neutral"

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

