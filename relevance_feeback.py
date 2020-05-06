"""
Title: Relevance Feedback

Project: CSI4107 Project
Version: Final System
Component: Module 4

Created: 26 Apr 2020

Author: Jonathan Boerger
Status: Completed

Description: This module captures user indicated relevance in VSM generated models.
This relevance is captured for the duration of a session(until the search engine is closed).
A user can indicate both relevant and non relevant documents.
The relevance information is stored in global variables (one fore each corpus).


Limitation:
    Since this module significantly interfaces with the GUI, and the fact that my GUI is imported, I was constrained
    within the existing GUI framework.

    Relevance is query specific, i.e. dog vs dogs will each have their own relevance information

General references:

    As detailled in the project report, I was unable to implement module 7. Therefore, I have adapted Tiffany Maynard
    GUI for her version of this project to work with this module. As a result, some methods are structured similarily
    to allow for intergration.
"""

from config import UOTTAWA
import config



def initialize_dicts():
    config.RELEVANCE_DICT_UOTTAWA = dict()
    config.RELEVANCE_DICT_REUTERS = dict()


def update_relevance(query_key, doc_id, corpus):
    """
    Implements in local memory relevance information as dictionary.
    Furthermore, this method also updates the relevance information based on positive and negative feedback from the user

    Relevance information is query specific.

    Reference:
        Adapted from Tiffiny Maynard, specifically the toggle functionality given the GUI structure.
    """
    # getting the relevant dict
    if corpus == UOTTAWA:
        current_dict = config.RELEVANCE_DICT_UOTTAWA
    else:
        current_dict = config.RELEVANCE_DICT_REUTERS

    # if there already is relevance information for the query
    if current_dict.get(query_key):
        relevance_list=current_dict[query_key]
        flag = 0

        #from relevant to not relevant
        if doc_id in relevance_list[0]:
            relevance_list[0].remove(doc_id)
            relevance_list[1].append(doc_id)
        #from non relevant to neutral
        elif doc_id in relevance_list[1]:
            relevance_list[1].remove(doc_id)
            # if there no longer is any relevance information for the given query, remove query from dict
            if relevance_list[0]==[] and relevance_list[1]==[]:
                del current_dict[query_key]
                flag=1
        # from neutral to relevant
        else:
            relevance_list[0].append(doc_id)
        # if there stil exist relevance information for the query, update the relevance dict
        if flag==0:
            current_dict[query_key]=relevance_list
    # if there is no relevance information, create a new entry in the relevance dictionary with indicating relevant
    else:
        current_dict[query_key]= [[doc_id], []]





def get_relevance(query_key, doc_id, corpus):
    """ Sourced from Tiffany Maynard since it is interacting with the GUI

    Getting relevance information for a query-doc_id pair
    """
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
    """
    Returning complete relevance information for a given query.
    To be utilized in other modules (mainly 5)
    """

    if corpus == UOTTAWA:
        current_dict = config.RELEVANCE_DICT_UOTTAWA
    else:
        current_dict = config.RELEVANCE_DICT_REUTERS
    return current_dict.get(query_key)





