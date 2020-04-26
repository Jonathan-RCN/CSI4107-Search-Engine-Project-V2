import ast
import csv

import config
import os

COMPLETION_LIST=[]

def get_bigram_from_csv(corpus):
    bigram_csv_file_name=config.CORPUS[corpus]['bigram_file']
    usable_bigram_dict=dict()
    if os.path.exists(bigram_csv_file_name):
        with open(bigram_csv_file_name, 'r') as file:
            csv.field_size_limit(100000000)
            reader = csv.reader(file)
            for row in reader:
                if row != []:
                    usable_bigram_dict[row[0]] = ast.literal_eval(row[1])
        return usable_bigram_dict

    else:
        print(f'There is no available bigram model currently available for {corpus}')
        return {}



def get_n_best_completion_pairs(n_gram_dict):
    for primary_word in n_gram_dict:
        secondary_word_list=list(n_gram_dict[primary_word])
        top_n_word_list=secondary_word_list[:config.QCM_MAX_NO_WORD_SUGGESTED]
        for secondary_word in top_n_word_list:
            completion_pair=f'{primary_word} {secondary_word}'
            global COMPLETION_LIST
            COMPLETION_LIST.append(completion_pair)

def translate_completion_list_to_static_csv(completion_list):
    csv_filename="qcm_complation_pair_list.csv"
    s = ','
    completion_string = s.join(completion_list)
    #print(completion_string.split(','))
    with open(csv_filename, 'w', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(completion_string.split(','))

def qcm_wrapper_creation():
    """Limitation: if there is a change in the confrim file (n-best QCM coount) or the n-graph model the completion list will not update // static"""
    uottawa_n_gram_dict=get_bigram_from_csv(config.UOTTAWA)
    get_n_best_completion_pairs(uottawa_n_gram_dict)
    reuter_n_gram_dict=get_bigram_from_csv(config.REUTERS)
    get_n_best_completion_pairs(reuter_n_gram_dict)
    global COMPLETION_LIST
    translate_completion_list_to_static_csv(COMPLETION_LIST)

def qcm_completion_list_access():
    # check if completion list still exist in memory as global variable
    global COMPLETION_LIST
    if COMPLETION_LIST !=[]:
        return COMPLETION_LIST
    else:
        csv_filenmae="qcm_complation_pair_list.csv"
        if os.path.exists(csv_filenmae):
            with open(csv_filenmae, newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                qcm_complation_pair_list = list(reader)
            return qcm_complation_pair_list[0]
        else:
            print(f'There is no available QCM completion pair list currently available')
            return []



qcm_wrapper_creation()



