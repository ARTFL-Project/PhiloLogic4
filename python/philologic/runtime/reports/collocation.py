#!/usr/bin/env python3
"""Collocation results"""

import os
import re
import timeit
import sqlite3
from collections import defaultdict
import string
import msgpack
import lz4.frame

from philologic.runtime.DB import DB
from philologic.runtime.Query import get_expanded_query

remove_punctuation_map = dict((ord(char), None) for char in string.punctuation if char != "'")


def collocation_results(request, config):
    """Fetch collocation results"""
    db = DB(config.db_path + "/data/")
    if request["collocate_distance"]:
        hits = db.query(request["q"], "proxy", int(request["collocate_distance"]), **request.metadata)
    else:
        hits = db.query(request["q"], "cooc", request["arg"], **request.metadata)
    hits.finish()
    collocation_object = {"query": dict([i for i in request])}

    try:
        collocate_distance = int(request["collocate_distance"])
    except ValueError:  # Getting an empty string since the keyword is not specificed in the URL
        collocate_distance = None

    if request.colloc_filter_choice == "nofilter":
        filter_list = []
    else:
        filter_list = build_filter_list(request, config)
    collocation_object["filter_list"] = filter_list
    filter_list = set(filter_list)

    # Build list of search terms to filter out
    query_words = []
    for group in get_expanded_query(hits):
        for word in group:
            word = word.replace('"', "")
            query_words.append(word)
    query_words = set(query_words)
    filter_list = filter_list.union(query_words)

    if request["collocate_distance"]:
        hits = db.query(request["q"], "proxy", int(request["collocate_distance"]), raw_results=True, **request.metadata)
    else:
        hits = db.query(request["q"], "proxy", request["arg"], raw_results=True, **request.metadata)
    hits.finish()
    return precompute_version(hits, config, request, db, filter_list, collocation_object)


def precompute_version(hits, config, request, db, filter_list, collocation_object):
    stored_sentence_id = None
    stored_sentence_counts = defaultdict(int)
    sentence_hit_count = 1
    hits_done = request.start or 0
    max_time = request.max_time or 2
    all_collocates = defaultdict(lambda: {"count": 0})
    cursor = db.dbh.cursor()
    start_time = timeit.default_timer()
    for hit in hits[hits_done:]:
        # start_byte = extract_bytes(hit)[0]
        sentence = " ".join(map(str, hit[:6])) + " 0"
        cursor.execute("SELECT words FROM sentences WHERE philo_id = ?", (sentence,))
        words = msgpack.loads(lz4.frame.decompress(cursor.fetchone()[0]))
        parent = hit[:6] + (0,)
        if parent != stored_sentence_id:
            sentence_hit_count = 1
            stored_sentence_id = parent
            stored_sentence_counts = defaultdict(int)
            for collocate in words:
                if collocate["word"] not in filter_list:
                    stored_sentence_counts[collocate["word"]] += 1
        else:
            sentence_hit_count += 1
        for word in stored_sentence_counts:
            if stored_sentence_counts[word] < sentence_hit_count:
                continue
            all_collocates[word]["count"] += 1
        hits_done += 1

        elapsed = timeit.default_timer() - start_time
        # avoid timeouts by splitting the query if more than request.max_time (in
        # seconds) has been spent in the loop
        if elapsed > int(max_time):
            break

    collocation_object["collocates"] = all_collocates
    collocation_object["results_length"] = len(hits)
    if hits_done < collocation_object["results_length"]:
        collocation_object["more_results"] = True
        collocation_object["hits_done"] = hits_done
    else:
        collocation_object["more_results"] = False
        collocation_object["hits_done"] = collocation_object["results_length"]

    return collocation_object


def extract_bytes(hit):
    remaining = list(hit[8:])
    byte_offsets = []
    while remaining:
        if remaining:
            byte_offsets.append(remaining.pop(0))
    byte_offsets.sort()
    return byte_offsets


def build_filter_list(request, config):
    """set up filtering with stopwords or most frequent terms."""
    if config.stopwords and request.colloc_filter_choice == "stopwords":
        if os.path.isabs(config.stopwords):
            filter_file = config.stopwords
        else:
            return ["stopwords list not found"]
        filter_num = float("inf")
    else:
        if request.colloc_filter_choice == "tfidf":
            filter_file = config.db_path + "/data/frequencies/words_mean_tfidf"
        else:
            filter_file = config.db_path + "/data/frequencies/word_frequencies"
        if request.filter_frequency:
            filter_num = int(request.filter_frequency)
        else:
            filter_num = 100  # default value in case it's not defined
    filter_list = [request["q"]]
    with open(filter_file, encoding="utf8") as filehandle:
        for line_count, line in enumerate(filehandle):
            if line_count == filter_num:
                break
            try:
                word = line.split()[0]
            except IndexError:
                continue
            filter_list.append(word)
    return filter_list
