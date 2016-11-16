#!/usr/bin/env python
"""Compute collocation scores"""

from math import log

def pointwise_mutual_information(total_word_count, collocate_count, collocate, cursor):
    """Calculate Pointwise Mutual Information."""
    if collocate_count < 5:
        return 0
    query = """select count(*) from words where philo_name='%s'""" % collocate
    cursor.execute(query)
    total_collocate_count = cursor.fetchone()[0]
    score = log(collocate_count / total_word_count * total_collocate_count)
    return score
