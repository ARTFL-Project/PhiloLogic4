#!/usr/bin/env python
"""Find similar words to query term."""

from __future__ import absolute_import
import os
import unicodedata

from philologic.Query import get_expanded_query
from Levenshtein import ratio


def get_all_words(db, request):
    """Expand query to all search terms."""
    words = request["q"].replace('"', '')
    hits = db.query(words)
    hits.finish()
    expanded_terms = get_expanded_query(hits)
    word_groups = []
    for word_group in expanded_terms:
        normalized_group = []
        for word in word_group:
            word = u''.join([i for i in unicodedata.normalize("NFKD", word.decode('utf8')) if not unicodedata.combining(i)]).encode("utf-8")
            normalized_group.append(word)
        word_groups.append(normalized_group)
    return word_groups

def find_similar_words(db, config, request):
    """Edit distance function."""
    query_groups = get_all_words(db, request)
    file_path = os.path.join(config.db_path, "data/frequencies/normalized_word_frequencies")
    new_query_groups = [set([]) for i in query_groups]
    with open(file_path) as fh:
        for line in fh:
            line = line.strip()
            try:
                normalized_word, regular_word = line.split('\t')
                for pos, query_group in enumerate(query_groups):
                    for query_word in query_group:
                        if ratio(query_word, normalized_word) >= float(request.approximate_ratio):
                            new_query_groups[pos].add(regular_word)
            except ValueError:
                pass
    return ' '.join([" | ".join(group) for group in new_query_groups])
