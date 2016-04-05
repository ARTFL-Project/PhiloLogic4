#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Parse term query before passing it to the PhiloLogic4 library."""


def parse_query(query_terms):
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

    return query_terms
