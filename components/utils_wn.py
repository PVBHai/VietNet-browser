# import nltk
# from nltk.corpus import wordnet as wn
import sqlite3

# ✅ Đặt thật sớm
_orig_connect = sqlite3.connect
def connect_threadsafe(*args, **kwargs):
    kwargs["check_same_thread"] = False
    return _orig_connect(*args, **kwargs)
sqlite3.connect = connect_threadsafe

import os
import wn

# Data
if not os.path.exists('./data'):
    os.mkdir('./data')

# Tải dữ liệu WordNet nếu chưa có
# nltk.download('wordnet')
from pathlib import Path
wn.config.data_directory = Path('./data')
wn.download('oewn:2024')

def get_relationships(synset, relationship_type):
    if relationship_type == 'hypernym':
        return synset.hypernyms()
    elif relationship_type == 'hyponym':
        return synset.hyponyms()
    elif relationship_type == 'meronym':
        return synset.part_meronyms() + synset.substance_meronyms()
    elif relationship_type == 'holonym':
        return synset.part_holonyms() + synset.substance_holonyms()
    return []
