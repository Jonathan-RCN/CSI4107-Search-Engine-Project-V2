"""
Access corpus of documents

Project: CSI4107 Project
Version: Vanilla System
Component: Module 5

Created: 26 Jan 2020
Last modified: 27 Apr 2020

Author: Tiffany Maynard
Modified: Jonatan Boerger
Status: Completed

Description: Access documents from the corpus

Modification: added functionality for topics and hendeling for cases when Reuters documents have nil content
"""

import xml.etree.ElementTree as xml
from bs4 import BeautifulSoup as bs
import os.path
import config


class Document:
    """Document holds all the document info from a corpus."""
    doc_id: int
    score: float
    title: str
    doctext: str
    topics: list

    def __init__(self, doc_id, score, title, doctext, topics):
        """Initialize document."""
        self.doc_id = doc_id
        self.score = score
        if title:
            self.title = title
        else:
            self.title = ''
        if doctext:
            self.doctext = doctext
        else:
            self.doctext = ''
        if topics:
            self.topics = topics
        else:
            self.topics = ''


# def get_documents(corpus, list_doc_ids):
#     """Return a list of documents using a given list of (doc_id, score)
#        order of doc ids is preserved."""
#     # XML parse code adapted from
#     # https://stackabuse.com/reading-and-writing-xml-files-in-python/
#     corpus_filename = config.CORPUS[corpus]['corpusxml']
#     if not os.path.isfile(corpus_filename):
#         print(corpus_filename + ' does not exist')
#         return []
#     doc_list = []
#     if corpus == config.UOTTAWA:
#         tree = xml.parse(corpus_filename)
#         root = tree.getroot()
#         #list_doc_ids is a list of (doc_id, score) pairs
#         for doc in list_doc_ids:
#             doc_id = doc[0]
#             #uOttawa index and doc_id are equal
#             doc_to_add = Document(doc_id, doc[1],
#                                   root[doc_id][0].text+' '+root[doc_id][1].text,
#                                   root[doc_id][2].text, [])
#             doc_list.append(doc_to_add)
#     else:
#         bs_corpus = get_reuters_corpus_as_bs(corpus_filename)
#         #reuters index and doc_id are different
#         for doc in list_doc_ids:
#             doc_id = doc[0]
#             doc_in_corpus = bs_corpus.find("article", {"doc_id":str(doc_id)})
#             doc_to_add = Document(doc_id, doc[1],
#                                   doc_in_corpus.find("title").text,
#                                   doc_in_corpus.find("topics").text+ '\n'
#                                   + doc_in_corpus.find("body").text,
#                                   doc_in_corpus.find("topics").text)
#             doc_list.append(doc_to_add)
#     return doc_list
#
# def get_reuters_corpus_as_bs(filename):
#     """to get reuters corpus as beautiful soup format"""
#     content = []
#     # Read the XML file
#     with open(filename, "r") as file:
#         # Read each line in the file, readlines() returns a list of lines
#         content = file.readlines()
#         # Combine the lines in the list into a string
#         content = "".join(content)
#         bs_content = bs(content, 'html.parser')
#         return bs_content




#
# class Document:
#     """Document holds all the document info from a corpus."""
#     doc_id: int
#     score: float
#     title: str
#     doctext: str
#     topics: list
#
#     def __init__(self, doc_id, score, title, doctext, topics):
#         """Initialize document."""
#         self.doc_id = doc_id
#         self.score = score
#         if title:
#             self.title = title
#         else:
#             self.title = '// There is no title information available. Reuters did not supply any title information for this article. //'
#         if doctext:
#             self.doctext = doctext
#         else:
#             self.doctext = '// There is no text body information available. Reuters did not supply any body text for this article. //'
#         if topics:
#             self.topics = topics
#         else:
#             self.topics = ['Nil']
#
#
def get_documents(corpus, list_doc_ids):
    """Return a list of documents using a given list of (doc_id, score)
       order of doc ids is preserved."""
    # XML parse code adapted from
    # https://stackabuse.com/reading-and-writing-xml-files-in-python/
    corpus_filename = config.CORPUS[corpus]['corpusxml']
    if not os.path.isfile(corpus_filename):
        print(corpus_filename + ' does not exist')
        return []
    tree = xml.parse(corpus_filename)
    root = tree.getroot()
    doc_list = []
    #list_doc_ids is a list of (doc_id, score) pairs
    for doc in list_doc_ids:
        doc_id = doc[0]
        # print(doc_id)
        # print(doc[1])
        # print(root[doc_id][0].text)
        if root[doc_id][1].text == None:
            root[doc_id][
                1].text = ' // There is no title information available. Reuters did not supply any title information for this article. //'
        if root[doc_id][2].text == None:
            root[doc_id][
                2].text = '// There is no text body information available. Reuters did not supply any body text for this article. //'
    # print(root[doc_id][1].text)
    # print(root[doc_id][2].text)
        if corpus==config.UOTTAWA:
            doc_to_add = Document(doc_id, doc[1],
                                  root[doc_id][0].text + ' ' + root[doc_id][1].text,
                                  root[doc_id][2].text, [])
            doc_list.append(doc_to_add)
        elif corpus ==config.REUTERS:
            if root[doc_id][3].text == None:
                root[doc_id][
                    3].text = '// There is no  topic information available. Reuters did not supply any body text for this article. //'

            doc_to_add = Document(doc_id, doc[1],
                                  root[doc_id][0].text + ' ' + root[doc_id][1].text,
                                  root[doc_id][2].text,root[doc_id][3].text)
            doc_list.append(doc_to_add)



    return doc_list
