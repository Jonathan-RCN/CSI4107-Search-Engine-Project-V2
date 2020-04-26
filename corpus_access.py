"""
Access corpus of documents

Project: CSI4107 Project
Version: Vanilla System
Component: Module 5

Created: 26 Jan 2020
Last modified: 13 Feb 2020

Author: Tiffany Maynard
Status: Completed

Description: Access documents from the corpus

"""
import xml.etree.ElementTree as xml
import os.path
import config


class Document:
    """Document holds all the document info from a corpus."""
    doc_id: int
    score: float
    title: str
    doctext: str

    def __init__(self, doc_id, score, title, doctext):
        """Initialize document."""
        self.doc_id = doc_id
        self.score = score
        self.title = title
        self.doctext = doctext


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
        doc_to_add = Document(doc_id, doc[1],
                              root[doc_id][0].text+' '+root[doc_id][1].text,
                              root[doc_id][2].text)
        doc_list.append(doc_to_add)
    return doc_list
