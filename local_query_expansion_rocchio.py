from datetime import datetime

import numpy as np

import config
import vsm_retrieval
import linguistic_processor
import relevance_feeback as RF


# np.set_printoptions(threshold=sys.maxsize, precision=8)

def transfrom_query_to_word_vector(query, corpus):
    inverted_index = vsm_retrieval.get_inverted_index(corpus)
    processed_query = linguistic_processor.linguistic_module(query, config.LINGUISTIC_PARAMS)
    query_word_vector = np.zeros((len(inverted_index)))
    for inverted_index_index, inverted_index_word in enumerate(inverted_index):
        if inverted_index_word in processed_query:
            query_word_vector[inverted_index_index] = 1

    return query_word_vector


def rocchio_wrapper(vsm_query, corpus):
    start_time = datetime.now()
    original_q0_vector = transfrom_query_to_word_vector(vsm_query, corpus)
    # for testing:
    # relevant_relevance_list, non_relevant_relevance_list=get_query_relevance_list(vsm_query, corpus)

    relevant_relevance_list, non_relevant_relevance_list = [0, 1], [3, 4]
    # /for testing
    relevant_Dr_vector_list = tranform_relevance_list_to_document_word_vector_list(relevant_relevance_list, corpus)
    non_relevant_Dnr_vector_list = tranform_relevance_list_to_document_word_vector_list(non_relevant_relevance_list,
                                                                                        corpus)

    return calculate_rocchio_modified_query_word_vector_weights(original_q0_vector, relevant_Dr_vector_list,
                                                                non_relevant_Dnr_vector_list,
                                                                vsm_query, relevant_relevance_list,
                                                                non_relevant_relevance_list, start_time)


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

    print(''.rjust(60, '/'))
    print('LQE and Rocchio information:')
    print(''.rjust(60, '='))

    print(f'Bellow are the heads of the relevant (doc ids: {relevant_rl})'
          f' document word vectors (Dr) where each vector is (Dj):')
    for dj in relevant_vector_list:
        print(f'{str(dj[:30])[:57]}...')
    print(''.rjust(60, '-'))
    print('These are then added together to a unified vecor:')
    print(f'{str(relevant_vector_list_sum[:30])[:57]}...')
    print(''.rjust(60, '-'))
    print(
        f'A beta factor of {beta_weight} (where beta is {config.LQE_ROCCHIO_BETA}) is then applied to create the positive feedback vector:')
    print(f'{str(positive_feedback[:30])[:57]}...')
    print(''.rjust(60, '='))
    print(f'Bellow are the heads of the non-relevant (doc ids: {non_relevant_rl})'
          f' document word vectors (Dnr) where each vector is (Dj):')
    for dj in non_relevant_vector_list:
        print(f'{str(dj[:30])[:57]}...')
    print(''.rjust(60, '-'))
    print('These are then added together to a unified vecor:')
    print(f'{str(non_relevant_vector_list_sum[:30])[:57]}...')
    print(''.rjust(60, '-'))
    print(
        f'A beta factor of {gamma_weight} (where beta is {config.LQE_ROCCHIO_GAMMA}) is then applied to create the negative feedback vector:')
    print(f'{str(negative_feedback[:30])[:57]}...')
    print(''.rjust(60, '='))
    print(f'Bellow is the head of the query ({query}) word vector (q0):')
    print(f'{str(original_vector[:30])[:57]}...')
    print(''.rjust(60, '-'))
    print(f'This is then tranformed int new mofied query word vector (qm) via Rocchio algorithm:')
    print(f'{str(modified_query_word_vector[:30])[:57]}...')
    print(''.rjust(60, '='))
    print(f'This took {(datetime.now() - start_time).seconds} seconds to calculate. ')
    print(''.rjust(60, '/'))

    return modified_query_word_vector


def get_query_relevance_list(query, corpus):
    query_relevance_list = RF.retreive_relevance_as_list(query, corpus)
    # relevant /non relevant
    return query_relevance_list[0], query_relevance_list[1]


def tranform_relevance_list_to_document_word_vector_list(relevance_list, corpus):
    inverted_index = vsm_retrieval.get_inverted_index(corpus)
    rl_doc_word_vec_list = []
    for doc_id in relevance_list:
        doc_specific_word_vector = transform_doc_id_to_document_word_vector(doc_id, corpus)
        rl_doc_word_vec_list.append(doc_specific_word_vector)
    return rl_doc_word_vec_list


def transform_doc_id_to_document_word_vector(doc_id, corpus):
    inverted_index = vsm_retrieval.get_inverted_index(corpus)
    doc_specific_word_vector = np.zeros(len(inverted_index))
    for inverted_index_index, inverted_index_word in enumerate(inverted_index):
        word_instance_dict = inverted_index[inverted_index_word].get(doc_id)
        if word_instance_dict != None:
            doc_specific_word_vector[inverted_index_index] = word_instance_dict['frequency']
        else:
            doc_specific_word_vector[inverted_index_index] = 0

    return doc_specific_word_vector

#
# rocchio_wrapper('student effect learn ', config.UOTTAWA)
# rocchio_wrapper('student effect learn ', config.REUTERS)

# def test(doc_id, corpus):
#     inverted_index = vsm_retrieval.get_inverted_index(corpus)
#     word_count=0
#     value_sum=0.0
#     for inverted_index_index, inverted_index_word in enumerate(inverted_index):
#         word_instance_dict = inverted_index[inverted_index_word].get(doc_id)
#         if word_instance_dict != None:
#              freq=word_instance_dict['frequency']
#              weight=word_instance_dict['weight']
#              word_count+=freq
#              value_sum+=freq*weight
#         else:
#             pass
#     if word_count==0: word_count=1
#     return word_count, value_sum, value_sum/word_count
#
# max_count=0
# max_score=0
# max_count_ratio=0
# max_score_ratio=0
# max_count_index=0
# max_score_index=0
# for x in range (0,664):
#
#
#     word_count, value_sum, ratio=test(x, config.UOTTAWA)
#     print(f'{x} --> {word_count, value_sum, ratio}')
#
#     if word_count>max_count:
#         max_count=word_count
#         max_count_ratio=ratio
#         max_count_index=x
#     if value_sum>max_score:
#         max_score=value_sum
#         max_score_ratio=ratio
#         max_score_index=x
#
# print(max_count, max_count_ratio, max_count_index)
#
# print(max_score, max_score_ratio, max_score_index)
#
#
#
# max_count=0
# max_score=0
# max_count_ratio=0
# max_score_ratio=0
# max_count_index=0
# max_score_index=0
# # with tqdm(total=20500) as pbar:
# #     for x in range (0,20500):
# #
# #
# #         word_count, value_sum, ratio=test(x, config.REUTERS)
# #         # print(f'{x} --> {word_count, value_sum, ratio}')
# #
# #         if word_count>max_count:
# #             max_count=word_count
# #             max_count_ratio=ratio
# #             max_count_index=x
# #         if value_sum>max_score:
# #             max_score=value_sum
# #             max_score_ratio=ratio
# #             max_score_index=x
# #         pbar.update(1)
# #
# # print(max_count, max_count_ratio, max_count_index)
# #
# # print(max_score, max_score_ratio, max_score_index)
# query='Design issues of advanced multiprocessor distributed operating systems: multiprocessor system architectures; process and object models; synchronization and message passing primitives; memory architectures and management; distributed file systems; protection and security; distributed concurrency control; deadlock; recovery; remote tasking; dynamic reconfiguration; performance measurement, modeling, and system tuning. This course is equivalent to COMP 5102 at Carleton University.'
# print(vsm_retrieval.retrieve(query, config.UOTTAWA))
#
# query_2='Danners Inc said it has agreed in principle for Indian LP, a partnership associated with Sherman Clay Group, to purchase 100,000 shares of redeemable voting junior preferred stock with a liquidation preference of 20 dlrs per share and cumulative dividends of 1.60 dlrs per share annually for two mln dlrs. It said the partnership would also receive detachable warrants to buy 1,600,000 common shares at 1.25 dlrs each, payable in cash or in junior preferred stock at the liquidation preference value. Danners said completion of the infusion would allow the partnership to name a majority of its board. In addition, Danners said it granted the partnership an option to buy 200,000 more common shares at 1.25 dlrs each, exercisable if it should fail to meet any condition connected with the transaction or if principal shareholders should accept a merger offer from another party. It said Danners family members owning 171,538 shares have granted options to Indian to buy their shares on similar terms and conditions. The company said the Danner family options provide that if the infusion is completed, the partnership will have the option starting six months later and ending in April 1992 to buy the shares at the last bid or last sales price, whichever is lower. Danners said the agreement is subject to a recapitalization by its bank group of outstanding loans, satisfactory company prospects, favorable opinon from an investment banker and closing by April 30, with possible extensions to no later than May 11. The company lost 529,000 dlrs in the prior year. Danners said it has terminated its use of LIFO inventory accounting, resulting in a restatement of its net worth as of February 1, 1986, the last day of its prior fiscal year, to 15.5 mln dlrs from 9,901,000 dlrs. But losses for the year just ended will result in a net worth deficiency at the end of that year of about 4,400,000 dlrs or eight dlrs per share. The company said it incurred unusual fourth quarter losses due to the previously-announced closing and disposition of 17 of its 35 3D discount department stores, inventory clearances and conversion to a new pricing and promotion system. The company said if it should fail to perform under the deal, it could be liable for all expenses incurred by the partnership. If it does perform but the infusion transaction collapses for another reason, it said it could be liable for up to 50,000 dlrs in expenses. It said the Danner family members who have agreed to the option have the ability to sell some or all of their shares to the partnership around the closing date at two dlrs each. Danners further said it expects to report a loss for the year ended January 31 of over 19 mln dlrs, substantially worse than it had expected. The company said it also incurred losses in the fourth quarter on the disposition of nonoperating assets. It said it expects to report results for the year soon. Danners said problems with its credit relationships, together with its losses for the year, resulted in its transaction with Indian, which is intended to alleviate its problems.'
#
# print(vsm_retrieval.retrieve(query_2, config.REUTERS))
