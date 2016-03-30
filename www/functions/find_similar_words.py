#!/usr/bin/env python

import os
import sys
import unicodedata

from web_config import WebConfig

from Levenshtein import ratio


def find_similar_words(word_to_match, request):
    """Edit distance function"""
    config = WebConfig()
    db = DB(config.db_path + '/data/')
    hits = db.query(request["q"], request["method"], request["arg"], **request.metadata)
    hits.finish()
    expanded_terms = get_expanded_query(hits)[0]
    words = []
    
    file_path = os.path.join(config.db_path, "data/frequencies/normalized_word_frequencies")
    word = word_to_match.decode("utf-8", 'ignore').lower()
    word = u''.join([i for i in unicodedata.normalize("NFKD", word) if not unicodedata.combining(i)]).encode("utf-8")
    results = set([word_to_match])
    with open(file_path) as infile:
        for w in infile:
            w = w.strip()
            w_norm = w.split()[0]
            w_orig = w.split()[1]
            if ratio(word, w_norm) >= 0.8 and w_orig not in results:
                results.add(w_orig)
    return ' | '.join(['"%s"' % i for i in results])
