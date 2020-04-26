
"""Configuration info."""
UOTTAWA = "uOttawa"
REUTERS = "Reuters"
CORPUS = dict()
BIGRAM_MODEL_REQUIRED_MIN_FREQ=dict()
RELEVANCE_DICT=dict()
CORPUS[UOTTAWA] = {"source" : "UofO_Courses.html",
                   "corpusxml" : "uottawa_corpus.xml",
                   "inverted_index_file" : "uottawa_inverted_index.csv",
                   "lpp_file" : "uottawa_lpp.csv",
                   "bigraph_file" : "uottawa_bigraph_index.csv",
                   "spelling_file" : "uottawa_spelling.csv",
                   "bigram_file" : "Reteurs/uottawa_bigram.csv",
                   "corpusxml_bigram": "../uottawa_corpus.xml",
                   # "relevance_dict" : RELEVANCE_DICT_UOTTAWA,
                   }
CORPUS[REUTERS] = {"source" : "Reteurs/UofO_Courses.html",
                   "corpusxml" : "Reteurs/reuters_corpus.xml",
                   "inverted_index_file" : "Reteurs/reuters_inverted_index.csv",
                   "lpp_file" : "Reteurs/reuters_lpp.csv",
                   "bigraph_file" : "Reteurs/reuters_bigraph_index.csv",
                   "spelling_file" : "Reteurs/reuters_spelling.csv",
                   # "relevance_dict" : RELEVANCE_DICT_REUTERS,
                   "doc_by_topic" : "Reteurs/reuters_doc_by_topic.csv",
                   "bigram_file" : "Reteurs/reuters_bigram.csv",
                   "corpusxml_bigram": "Reteurs/reuters_corpus.xml",}

BIGRAM_MODEL_REQUIRED_MIN_FREQ[UOTTAWA]=0
BIGRAM_MODEL_REQUIRED_MIN_FREQ[REUTERS]=4


QCM_MAX_NO_WORD_SUGGESTED=5

QEM_MIN_WORD_TYPE_DISTR_RATIO=0.5
QEM_MAX_QUERY_WORD_LEN_FOR_EXP=3
QEM_MAX_TOTAL_WORD_COUNT=9

K_RETRIEVAL = 20
TOP_N_SPELLING = 3
LINGUISTIC_PARAMS = {"do_contractions": True,
                     "do_normalize_hyphens": True,
                     "do_normalize_periods": True,
                     "do_remove_punctuation": True,
                     "do_case_fold": True,
                     "do_stop_word_removal": True,
                     "do_stemming": True,
                     "do_lemming": False}

BIGRAM_MODEL_LINGUISTIC_PARAMS=LINGUISTIC_PARAMS
BIGRAM_MODEL_LINGUISTIC_PARAMS["do_stemming"]=False
BIGRAM_MODEL_LINGUISTIC_PARAMS["do_lemming"]=False


