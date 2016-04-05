#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Parse term query before passing it to the PhiloLogic4 library."""

import re
import find_similar_words


terms_split = re.compile(r'[\|| NOT | ]')


def parse_query(query_terms, request):
    """Parse query function."""
    # Allow use of OR as a boolean operator
    query_terms = query_terms.replace(' OR ', ' | ')

    # Remove typical punctuation
    query_terms = query_terms.replace("'", " ")
    query_terms = query_terms.replace(';', '')
    query_terms = query_terms.replace(',', '')
    query_terms = query_terms.replace('!', '')

    # Japanese special case
    query_terms = query_terms.replace('　', ' ')
    query_terms = query_terms.replace('｜', '|')
    query_terms = query_terms.replace('”', '"')
    query_terms = query_terms.replace('－', '-')
    query_terms = query_terms.replace('＊', '*')

    # Fuzzy matching, but only for one word
    query_length = len([i for i in terms_split.split(query_terms) if i])
    if request.approximate and query_length == 1:
        query_terms = find_similar_words(query_terms, request)

    import sys
    print >> sys.stderr, "PARSED QUERY TERMS", query_terms
    return query_terms
