#!/usr/bin/env python
"""Find similar words to query term."""

import os
import unicodedata

from Levenshtein import ratio


def find_similar_words(word_to_match, config, request):
    """Edit distance function."""
    file_path = os.path.join(config.db_path, "data/frequencies/normalized_word_frequencies")
    word = word_to_match.decode("utf-8", 'ignore').lower()
    word = u''.join([i for i in unicodedata.normalize("NFKD", word) if not unicodedata.combining(i)]).encode("utf-8")
    results = set([word_to_match])
    with open(file_path) as infile:
        for w in infile:
            w = w.strip()
            try:
                w_norm, w_orig = w.split('\t')
                if ratio(word, w_norm) >= float(request.approximate_ratio) and w_orig not in results:
                    results.add(w_orig)
            except ValueError:
                pass
    return ' | '.join(['"%s"' % i for i in results])
