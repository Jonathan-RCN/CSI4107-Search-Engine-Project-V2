import config
import os
import xml.etree.ElementTree as xml
from datetime import datetime
from tqdm import tqdm
import vsm_retrieval
import math
import csv

TOPIC_DICT = dict()
CLASSIFIED_DICT = dict()
CLASSIFIED_DICT_VAL = dict()


def get_topics():
    xml_corpus_filename = config.CORPUS[config.REUTERS]['corpusxml']
    tree = xml.parse(xml_corpus_filename)
    root = tree.getroot()
    complete_list = []
    topics_list_complete=[]
    uncategorized_list = []

    for doc_id in range(0, 21578):
        topic_list = root[doc_id][3].text
        if topic_list == None:
            topic_list = ["unspecified"]
            uncategorized_list.append(doc_id)
        else:
            topic_list = topic_list.split()
        complete_list.append(doc_id)
        for topic in topic_list:
            add_topic_to_dict(TOPIC_DICT, topic, doc_id)
            if topic not in topics_list_complete:
                topics_list_complete.append(topic)

    print(topics_list_complete)

    TOPIC_DICT["all_topics"] = complete_list
    return uncategorized_list

def topic_list_to_csv():
    get_topics()
    csv_filename = config.CORPUS[config.REUTERS]['doc_by_topic']
    with open(csv_filename, 'w') as file:
        writer = csv.writer(file)
        for key, value in TOPIC_DICT.items():
            writer.writerow([key, value])


def get_topic_information():
    return TOPIC_DICT

def knn_classifier_strict(unspecified_doc_list):
    # CLASSIFIED_DICT=dict()
    xml_corpus_filename = config.CORPUS[config.REUTERS]['corpusxml']
    tree = xml.parse(xml_corpus_filename)
    root = tree.getroot()
    not_able_to_classify = []
    un_classifiable = []
    progress_index = 1
    for doc_id in unspecified_doc_list:
        print(f' Processing doc id {doc_id} which is number {progress_index} or {len(unspecified_doc_list)}')
        progress_index += 1
        non_catg_doc_count = 0
        temp_topic_dict = dict()
        doc_text_query = root[doc_id][2].text
        if doc_text_query == None:
            doc_text_query = root[doc_id][1].text
            print('Not text body, using title instead.')
            if doc_text_query == None:
                un_classifiable.append(doc_id)
                print('Non classifiable, continueing to next document')
                # pbar.update(1)
                continue
        k_nearest_neaigbors = vsm_retrieval.knn_retrieve(doc_text_query)
        k_nearest_neaigbors = k_nearest_neaigbors[:config.KNN_K_VALUES]
        # print(k_nearest_neaigbors)
        for nn_doc_id in k_nearest_neaigbors:
            nn_topic_list = root[nn_doc_id][3].text
            if nn_topic_list == None:
                print('A non categorized document has been returned')
                non_catg_doc_count += 1
            else:
                nn_topic_list = nn_topic_list.split()
                for topic in nn_topic_list:
                    add_topic_to_dict(temp_topic_dict, topic, nn_doc_id)
        classified_topics = determine_topic(temp_topic_dict, non_catg_doc_count, doc_id)
        if classified_topics == []:
            not_able_to_classify.append(doc_id)
        else:
            # print(doc_id)
            # print(classified_topics)
            add_topic_to_dict(CLASSIFIED_DICT, doc_id, classified_topics)
            # print(CLASSIFIED_DICT)
    return not_able_to_classify


def knn_classifier_tolerant(unspecified_doc_list):
    # CLASSIFIED_DICT=dict()
    xml_corpus_filename = config.CORPUS[config.REUTERS]['corpusxml']
    tree = xml.parse(xml_corpus_filename)
    root = tree.getroot()
    not_able_to_classify = []
    un_classifiable = []
    progress_index = 1
    for doc_id in unspecified_doc_list:
        print(f' Processing doc id {doc_id} which is number {progress_index} or {len(unspecified_doc_list)}')
        progress_index += 1
        non_catg_doc_count = 0
        temp_topic_dict = dict()
        doc_text_query = root[doc_id][2].text
        if doc_text_query == None:
            doc_text_query = root[doc_id][1].text
            print('Not text body, using title instead.')
            if doc_text_query == None:
                un_classifiable.append(doc_id)
                print('Non classifiable, continueing to next document')
                # pbar.update(1)
                continue
        k_nearest_neaigbors = vsm_retrieval.knn_retrieve(doc_text_query)
        k_nn_count = 0
        for nn_doc_id in k_nearest_neaigbors:
            nn_topic_list = root[nn_doc_id][3].text
            if nn_topic_list == None:
                continue
            else:
                k_nn_count += 1
                nn_topic_list = nn_topic_list.split()
                for topic in nn_topic_list:
                    add_topic_to_dict(temp_topic_dict, topic, nn_doc_id)
            if k_nn_count == config.KNN_K_VALUES:
                break
        # print(k_nearest_neaigbors)
        classified_topics = determine_topic(temp_topic_dict, non_catg_doc_count, doc_id)
        if classified_topics == []:
            not_able_to_classify.append(doc_id)
        else:
            # print(doc_id)
            # print(classified_topics)
            add_topic_to_dict(CLASSIFIED_DICT, doc_id, classified_topics)
            # print(CLASSIFIED_DICT)
    return not_able_to_classify


def determine_topic(topic_dict, non_catg_doc_count, doc_id):
    topic_count_threshold = math.ceil(config.KNN_K_VALUES / 2)
    classidied_topics = []
    if non_catg_doc_count == 0:
        for key, topic in enumerate(topic_dict):
            if len(topic_dict[topic]) >= topic_count_threshold:
                print(f'{doc_id} has been classified as {topic}')
                classidied_topics.append(topic)
                print(classidied_topics)
        return classidied_topics
    else:
        for key, topic in enumerate(topic_dict):
            topic_count = len(topic_dict[topic])
            if topic_count >= topic_count_threshold:
                print(f'{doc_id} has been classified as {topic}')
                classidied_topics.append(topic)
            elif topic_count < topic_count_threshold and topic_count >= topic_count_threshold - non_catg_doc_count:
                # print(''.rjust(15, '='))
                # print(f'Given that {non_catg_doc_count} uncategorized document exist in the {config.KNN_K_VALUES} nearest neighbor of doc_id {doc_id}, '
                #       f'there currently is too much ambiguity in the knn topic count to determine a topic for '
                #       f'this document.')
                print(f'Document {doc_id} will require another pass to categorize.')
                # print(''.rjust(15, '='))
                return []
        return classidied_topics


def update_corpus(speficied_dict):
    print(f'Updating the corpus')
    xml_corpus_filename = config.CORPUS[config.REUTERS]['corpusxml']
    tree = xml.parse(xml_corpus_filename)
    root = tree.getroot()
    # print(speficied_dict)
    with open(xml_corpus_filename, "wb") as file:
        for key, doc_id in enumerate(speficied_dict):
            topic_list_list = speficied_dict[doc_id]
            topic_string = " ".join(topic_list_list[0])
            # print(root[doc_id][1].text)
            # print(topic_string)
            root[doc_id][3].text = topic_string
        tree = xml.ElementTree(root)
        tree.write(file)
    print(f'Finished updating the corpus')


def multipass_wrapper(doc_id_list_for_catg, max_pass, knn_method):
    CLASSIFIED_DICT.clear()
    previous_unclass = []
    if knn_method == 'tolerant':
        remaning_unclass = knn_classifier_tolerant(doc_id_list_for_catg)
    else:
        remaning_unclass = knn_classifier_strict(doc_id_list_for_catg)

    update_corpus(CLASSIFIED_DICT)

    for x in range(1, config.KNN_MAX_PASS):
        CLASSIFIED_DICT.clear()
        print(remaning_unclass)
        if knn_method == 'tolerant':
            remaning_unclass = knn_classifier_tolerant(remaning_unclass)
        else:
            remaning_unclass = knn_classifier_strict(remaning_unclass)

        if remaning_unclass == []:
            print('All documents have been classified')
            break
        if remaning_unclass == previous_unclass:
            print('There has been no increased classifaction, quitting')
            break
        update_corpus(CLASSIFIED_DICT)
        previous_unclass = remaning_unclass

    topic_list_to_csv()


def add_topic_to_dict(dictionary, key, value):
    if dictionary.get(key):
        topic_doc_id_list = dictionary.get(key)
        topic_doc_id_list.append(value)
        dictionary[key] = topic_doc_id_list
    else:
        dictionary[key] = [value]


def validate_knn_strict(specified_topic_list):
    print(specified_topic_list)
    xml_corpus_filename = config.CORPUS[config.REUTERS]['corpusxml']
    tree = xml.parse(xml_corpus_filename)
    root = tree.getroot()
    not_able_to_classify = []
    classified_exact_match = []
    classified_partial_match = []
    classified_no_mathch = []
    un_classifiable = []
    with tqdm(total=len(specified_topic_list)) as pbar:
        for doc_id in specified_topic_list:
            non_catg_doc_count = 0
            temp_topic_dict = dict()
            doc_text_query = root[doc_id][2].text
            if doc_text_query == None:
                doc_text_query = root[doc_id][1].text
                print('Not text body, using title instead.')
                if doc_text_query == None:
                    un_classifiable.append(doc_id)
                    print('Non classifiable, continueing to next document')
                    pbar.update(1)
                    continue
            k_nearest_neaigbors = vsm_retrieval.knn_retrieve(doc_text_query)
            k_nearest_neaigbors = k_nearest_neaigbors[:config.KNN_K_VALUES]
            print(f' {doc_id} --> {k_nearest_neaigbors}')
            for nn_doc_id in k_nearest_neaigbors:
                nn_topic_list = root[nn_doc_id][3].text
                if nn_topic_list == None:
                    # print('A non categorized document has been returned')
                    non_catg_doc_count += 1
                else:
                    nn_topic_list = nn_topic_list.split()
                    for topic in nn_topic_list:
                        add_topic_to_dict(temp_topic_dict, topic, nn_doc_id)

            classified_topics = determine_topic(temp_topic_dict, non_catg_doc_count, doc_id)
            if classified_topics == []:
                not_able_to_classify.append(doc_id)
            else:
                add_topic_to_dict(CLASSIFIED_DICT_VAL, doc_id, classified_topics)

                original_classification = root[doc_id][3].text.split()
                is_match = 0
                is_break = 0
                for topics in classified_topics:
                    if topics in original_classification:
                        is_match = 1
                    else:
                        is_break = 1
                        break
                if is_match == 1 and is_break == 0:
                    classified_exact_match.append(doc_id)
                elif is_match == 1 and is_break == 1:
                    classified_partial_match.append(doc_id)
                else:
                    classified_no_mathch.append(doc_id)
            pbar.update(1)
    speficied_len = len(specified_topic_list) - len(un_classifiable) - len(not_able_to_classify)
    if speficied_len == 0: speficied_len = 1
    print(f'The are {len(not_able_to_classify)} documents which no classification determination was possible.')
    print(f'There are {len(un_classifiable)} documents which there is no text available for classification.')
    print(
        f'The number of exact matches: {len(classified_exact_match)} || {len(classified_exact_match) / speficied_len}')
    print(
        f'The number of partial matches: {len(classified_partial_match)} || {len(classified_partial_match) / speficied_len}')
    print(
        f'The number of non matches: {len(classified_no_mathch)} || {len(classified_no_mathch) / speficied_len}')
    return not_able_to_classify


def validate_knn_tolerant(specified_topic_list):
    xml_corpus_filename = config.CORPUS[config.REUTERS]['corpusxml']
    tree = xml.parse(xml_corpus_filename)
    root = tree.getroot()
    not_able_to_classify = []
    classified_exact_match = []
    classified_partial_match = []
    classified_no_mathch = []
    un_classifiable = []
    with tqdm(total=len(specified_topic_list)) as pbar:
        for doc_id in specified_topic_list:
            non_catg_doc_count = 0
            temp_topic_dict = dict()
            doc_text_query = root[doc_id][2].text
            if doc_text_query == None:
                doc_text_query = root[doc_id][1].text
                print('Not text body, using title instead.')
                if doc_text_query == None:
                    un_classifiable.append(doc_id)
                    print('Non classifiable, continueing to next document')
                    pbar.update(1)
                    continue
            k_nearest_neaigbors = vsm_retrieval.knn_retrieve(doc_text_query)
            print(f' {doc_id} --> {k_nearest_neaigbors}')
            k_nn_count = 0
            for nn_doc_id in k_nearest_neaigbors:
                nn_topic_list = root[nn_doc_id][3].text
                if nn_topic_list == None:
                    continue
                else:
                    k_nn_count += 1
                    nn_topic_list = nn_topic_list.split()
                    for topic in nn_topic_list:
                        add_topic_to_dict(temp_topic_dict, topic, nn_doc_id)
                if k_nn_count == config.KNN_K_VALUES:
                    break

            classified_topics = determine_topic(temp_topic_dict, non_catg_doc_count, doc_id)
            if classified_topics == []:
                not_able_to_classify.append(doc_id)
            else:
                add_topic_to_dict(CLASSIFIED_DICT_VAL, doc_id, classified_topics)

                original_classification = root[doc_id][3].text.split()
                is_match = 0
                is_break = 0
                for topics in classified_topics:
                    if topics in original_classification:
                        is_match = 1
                    else:
                        is_break = 1
                        break
                if is_match == 1 and is_break == 0:
                    classified_exact_match.append(doc_id)
                elif is_match == 1 and is_break == 1:
                    classified_partial_match.append(doc_id)
                else:
                    classified_no_mathch.append(doc_id)
            pbar.update(1)
    speficied_len = len(specified_topic_list) - len(un_classifiable) - len(not_able_to_classify)
    if speficied_len == 0: speficied_len = 1
    print(f'The are {len(not_able_to_classify)} documents which no classification determination was possible.')
    print(f'There are {len(un_classifiable)} documents which there is no text available for classification.')
    print(
        f'The number of exact matches: {len(classified_exact_match)} || {len(classified_exact_match) / speficied_len}')
    print(
        f'The number of partial matches: {len(classified_partial_match)} || {len(classified_partial_match) / speficied_len}')
    print(
        f'The number of non matches: {len(classified_no_mathch)} || {len(classified_no_mathch) / speficied_len}')
    return not_able_to_classify


def multipass_wrapper_validate(doc_id_list_for_catg, max_pass, knn_method):
    # initial pass
    previous_unclass = []
    if knn_method == 'tolerant':
        remaning_unclass = validate_knn_tolerant(doc_id_list_for_catg)
    else:
        remaning_unclass = validate_knn_strict(doc_id_list_for_catg)
    update_corpus(CLASSIFIED_DICT_VAL)

    for x in range(1, max_pass):
        print(remaning_unclass)
        if knn_method == 'tolerant':
            remaning_unclass = validate_knn_tolerant(doc_id_list_for_catg)
        else:
            remaning_unclass = validate_knn_strict(doc_id_list_for_catg)
        update_corpus(CLASSIFIED_DICT_VAL)

        if remaning_unclass == []:
            print('All documents have been classified')
            break
        if remaning_unclass == previous_unclass:
            print('There has been no increased classifaction, quitting')
            break
        previous_unclass = remaning_unclass

get_topics()

# categorized_list = get_topics()
# # print(categorized_list[:100])
# # print(type(categorized_list[:100]))
# # result=validate_knn_single_pass(categorized_list[:100])
# # print(result)
# # print(type(result))
# multipass_wrapper([2, 3], 3, config.KNN_SELECTED_METHOD)
