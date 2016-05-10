#!/usr/bin/env python

import sys
sys.path.append('..')
from functions.wsgi_handler import WSGIHandler
from philologic.DB import DB
from wsgiref.handlers import CGIHandler
from reports.word_property_filter import get_word_attrib
import functions as f
import simplejson as json
import timeit


def generate_word_frequency(hits, q, db, config):
    """reads through a hitlist. looks up q["field"] in each hit, and builds up a list of
       unique values and their frequencies."""
    field = q["field"]
    counts = {}
    frequency_object = {}
    more_results = True
    start_time = timeit.default_timer()
    last_hit_done = q.start
    try:
        for n in hits[q.start:]:
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
        for k, v in counts.iteritems():
            url = f.link.make_absolute_query_link(
                config,
                q,
                start="0",
                end="0",
                report="word_property_filter",
                word_property=field,
                word_property_value=k)
            table[k] = {'count': v, 'url': url}

        frequency_object['results'] = table
        frequency_object["hits_done"] = last_hit_done
        if last_hit_done == len(hits):
            frequency_object['more_results'] = False
        else:
            frequency_object['more_results'] = True

    except IndexError:
        frequency_object['results'] = {}
        frequency_object['more_results'] = False

    frequency_object['results_length'] = len(hits)
    frequency_object['query'] = dict([i for i in q])

    return frequency_object


def get_frequency(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),
               ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    hits = db.query(request["q"], request["method"], request["arg"],
                    **request.metadata)
    word_frequency_object = generate_word_frequency(
        hits, request, db, config)
    yield json.dumps(word_frequency_object)


if __name__ == "__main__":
    CGIHandler().run(get_frequency)
