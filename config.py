"""Configuration info."""
UOTTAWA = "uOttawa"
REUTERS = "Reuters"
CORPUS = dict()
BIGRAM_MODEL_REQUIRED_MIN_FREQ = dict()
RELEVANCE_DICT = dict()

CORPUS[UOTTAWA] = {"source": "UofO_Courses.html",
                   "corpusxml": "uottawa_corpus.xml",
                   "inverted_index_file": "uottawa_inverted_index.csv",
                   "lpp_file": "uottawa_lpp.csv",
                   "bigraph_file": "uottawa_bigraph_index.csv",
                   "spelling_file": "uottawa_spelling.csv",
                   "bigram_file": "Reteurs/uottawa_bigram.csv",
                   "corpusxml_bigram": "uottawa_corpus.xml",
                   # "relevance_dict" : RELEVANCE_DICT_UOTTAWA,
                   }
CORPUS[REUTERS] = {"source": "Reteurs/UofO_Courses.html",
                   "corpusxml": "reuters_corpus.xml",
                   "inverted_index_file": "reuters_inverted_index.csv",
                   "lpp_file": "reuters_lpp.csv",
                   "bigraph_file": "reuters_bigraph_index.csv",
                   "spelling_file": "reuters_spelling.csv",
                   # "relevance_dict" : RELEVANCE_DICT_REUTERS,
                   "doc_by_topic": "reuters_doc_by_topic.csv",
                   "bigram_file": "reuters_bigram.csv",
                   "corpusxml_bigram": "reuters_corpus.xml", }

BIGRAM_MODEL_REQUIRED_MIN_FREQ[UOTTAWA] = 0
BIGRAM_MODEL_REQUIRED_MIN_FREQ[REUTERS] = 4

RELEVANCE_DICT_UOTTAWA = dict()
RELEVANCE_DICT_REUTERS = dict()

QCM_MAX_NO_WORD_SUGGESTED = 5

QEM_MIN_WORD_TYPE_DISTR_RATIO = 0.5
QEM_MAX_QUERY_WORD_LEN_FOR_EXP = 3
QEM_MAX_TOTAL_WORD_COUNT = 9

LQE_ROCCHIO_ALPHA = 1
LQE_ROCCHIO_BETA = 0.75
LQE_ROCCHIO_GAMMA = 0.15
LQE_ROCCHIO_MIN_TOLERANCE = 0.3

K_RETRIEVAL = 20
TOP_N_SPELLING = 5
LINGUISTIC_PARAMS = {"do_contractions": True,
                     "do_normalize_hyphens": True,
                     "do_normalize_periods": True,
                     "do_remove_punctuation": True,
                     "do_case_fold": True,
                     "do_stop_word_removal": True,
                     "do_stemming": True,
                     "do_lemming": False}

BIGRAM_MODEL_LINGUISTIC_PARAMS = {"do_contractions": True,
                                  "do_normalize_hyphens": True,
                                  "do_normalize_periods": True,
                                  "do_remove_punctuation": True,
                                  "do_case_fold": True,
                                  "do_stop_word_removal": True,
                                  "do_stemming": False,
                                  "do_lemming": False}

KNN_K_VALUES = 5
KNN_MAX_PASS = 5

TOLERANT = 'tolerant'
STRICT = 'stirct'

KNN_SELECTED_METHOD = TOLERANT

TOPICS_LIST = ["all_topics", 'cocoa', 'unspecified', 'earn', 'grain,', 'wheat,', 'corn,', 'barley,', 'oat,', 'sorghum',
               'veg-oil,', 'linseed,', 'lin-oil,', 'soy-oil,', 'sun-oil,', 'soybean,', 'oilseed,', 'sunseed,',
               'sorghum,', 'wheat', 'acq', 'earn,', 'grain', 'copper', 'housing', 'money-supply', 'coffee', 'acq,',
               'ship', 'sugar', 'trade', 'reserves', 'corn', 'meal-feed,', 'soy-meal', 'rye,', 'oilseed', 'cotton',
               'carcass,', 'livestock', 'crude', 'nat-gas', 'cpi,', 'gnp', 'oat', 'cpi', 'money-fx,', 'interest',
               'gnp,', 'bop', 'rice', 'red-bean,', 'rice,', 'sugar,', 'rubber,', 'copra-cake,', 'palm-oil,',
               'palmkernel,', 'coffee,', 'tea,', 'plywood,', 'soy-meal,', 'money-fx', 'copra-cake', 'alum', 'palm-oil',
               'cocoa,', 'soybean', 'gold,', 'platinum,', 'strategic-metal', 'tapioca', 'tin', 'trade,', 'rapeseed,',
               'groundnut-oil', 'gold', 'rape-oil,', 'tapioca,', 'cornglutenfeed,', 'citruspulp,', 'rape-meal',
               'crude,', 'barley', 'wool,', 'dlr', 'livestock,', 'l-cattle', 'retail', 'platinum', 'ipi', 'silver',
               'iron-steel', 'rubber', 'hog', 'propane,', 'heat,', 'gas', 'heat', 'jobs', 'lei', 'yen,', 'saudriyal',
               'interest,', 'zinc', 'carcass', 'rapeseed', 'veg-oil', 'orange', 'cotton,', 'pet-chem', 'dlr,', 'bop,',
               'gas,', 'fuel', 'nat-gas,', 'ship,', 'yen', 'reserves,', 'silver,', 'wpi', 'potato,', 'hog,', 'copper,',
               'lead,', 'zinc,', 'groundnut,', 'l-cattle,', 'can', 'groundnut', 'fishmeal,', 'meal-feed', 'jobs,',
               'ipi,', 'income,', 'money-supply,', 'palladium,', 'nickel,', 'lumber', 'nickel', 'fuel,', 'jet',
               'instal-debt', 'dfl', 'dmk', 'pet-chem,', 'fishmeal', 'lead', 'stg', 'potato', 'stg,', 'coconut-oil',
               'lumber,', 'plywood', 'corn-oil,', 'rape-oil', 'retail,', 'sunseed', 'inventories', 'wpi,', 'soy-oil',
               'iron-steel,', 'cpu', 'peseta', 'austdlr,', 'austdlr', 'housing,', 'cotton-oil', 'naphtha,', 'nzdlr',
               'income', 'rand', 'jet,', 'pork-belly', 'ringgit', 'coconut', 'inventories,', 'sun-oil', 'saudriyal,',
               'castorseed,', 'castor-oil', 'propane', 'lit', 'rupiah,', 'dmk,', 'nzdlr,', 'alum,', 'tin,', 'coconut,',
               'skr,', 'nkr,', 'dkr,', 'sun-meal,', 'lin-meal,', 'wool', 'tea', 'cruzado,', 'can,', 'strategic-metal,',
               'palladium', 'groundnut-oil,', 'cotton-oil,', 'cottonseed,', 'f-cattle,', 'orange,', 'bfr,',
               'pork-belly,', 'hk,', 'lei,', 'sfr,', 'dfl,', 'naphtha', 'coconut-oil,', 'nkr']
