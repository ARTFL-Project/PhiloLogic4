#!/usr/bin/env python3
"""Generate word frequency
Currently unmaintained."""

import timeit

from philologic5.runtime.link import make_absolute_query_link
from philologic5.runtime.DB import DB


def generate_word_frequency(request, config):
    """reads through a hitlist. looks up request["field"] in each hit, and builds up a list of
       unique values and their frequencies."""
    db = DB(config.db_path + "/data/")
    hits = db.query(request["q"], request["method"], request["arg"], **request.metadata)
    field = request["field"]
    counts = {}
    frequency_object = {}
    start_time = timeit.default_timer()
    last_hit_done = request.start
    try:
        for n in hits[request.start :]:
            key = get_word_attrib(n, field, db)
            if not key:
                # NULL is a magic value for queries, don't change it
                # recklessly.
                key = "NULL"
            if key not in counts:
                counts[key] = 0
            counts[key] += 1
            elapsed = timeit.default_timer() - start_time
            last_hit_done += 1
            if elapsed > 5:
                break

        table = {}
        for k, v in counts.items():
            url = make_absolute_query_link(
                config,
                request,
                start="0",
                end="0",
                report="word_property_filter",
                word_property=field,
                word_property_value=k,
            )
            table[k] = {"count": v, "url": url}

        frequency_object["results"] = table
        frequency_object["hits_done"] = last_hit_done
        if last_hit_done == len(hits):
            frequency_object["more_results"] = False
        else:
            frequency_object["more_results"] = True

    except IndexError:
        frequency_object["results"] = {}
        frequency_object["more_results"] = False

    frequency_object["results_length"] = len(hits)
    frequency_object["query"] = dict([i for i in request])

    return frequency_object


def get_word_attrib(n, field, db):
    """Get word attribute"""
    words = n.words
    key = field
    if key == "token":
        key = "philo_name"
    if key == "morph":
        key = "pos"
    val = ""
    for word in words:
        word_obj = word
        if val:
            val += "_"
        if word_obj[key]:
            val += word_obj[key]
        else:
            val += "NULL"

    if isinstance(val, str):
        return val.encode("utf-8")
    return val
