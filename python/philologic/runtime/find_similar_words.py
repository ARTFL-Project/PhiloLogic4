#!/usr/bin/env python3
"""Find similar words to query term."""


import hashlib
import os
import unicodedata

from philologic.Query import get_expanded_query
from Levenshtein import ratio


def get_all_words(db, request):
    """Expand query to all search terms."""
    words = request["q"].replace('"', "")
    hits = db.query(words)
    hits.finish()
    expanded_terms = get_expanded_query(hits)
    word_groups = []
    for word_group in expanded_terms:
        normalized_group = []
        for word in word_group:
            word = "".join([i for i in unicodedata.normalize("NFKD", word) if not unicodedata.combining(i)])
            normalized_group.append(word)
        word_groups.append(normalized_group)
    return word_groups


def find_similar_words(db, config, request):
    """Edit distance function."""
    # Check if lookup is cached
    hashed_query = hashlib.sha256()
    hashed_query.update(request["q"].encode("utf8"))
    hashed_query.update(str(request.approximate_ratio).encode("utf8"))
    approximate_filename = os.path.join(config.db_path, "data/hitlists/%s.approximate_terms" % hashed_query.hexdigest())
    if os.path.isfile(approximate_filename):
        with open(approximate_filename, encoding="utf8") as fh:
            approximate_terms = fh.read().strip()
            return approximate_terms
    query_groups = get_all_words(db, request)
    file_path = os.path.join(config.db_path, "data/frequencies/normalized_word_frequencies")
    new_query_groups = [set([]) for i in query_groups]
    with open(file_path, encoding="utf8") as fh:
        for line in fh:
            line = line.strip()
            try:
                normalized_word, regular_word = line.split("\t")
                for pos, query_group in enumerate(query_groups):
                    for query_word in query_group:
                        if ratio(query_word, normalized_word) >= float(request.approximate_ratio):
                            new_query_groups[pos].add(regular_word)
            except ValueError:
                pass
    new_query_groups = " ".join([" | ".join(group) for group in new_query_groups])
    cached_file = open(approximate_filename, "w", encoding="utf8")
    cached_file.write(new_query_groups)
    return new_query_groups
