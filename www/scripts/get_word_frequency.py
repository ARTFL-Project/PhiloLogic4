#!/usr/bin/env python

import sys
sys.path.append('..')
from functions.wsgi_handler import WSGIHandler
from philologic.DB import DB
from wsgiref.handlers import CGIHandler
from reports.word_property_filter import get_word_attrib
import functions as f
try:
    import simplejson as json
except ImportError:
    import json


def generate_word_frequency(hits, q, db, config):
    """reads through a hitlist. looks up q["field"] in each hit, and builds up a list of
       unique values and their frequencies."""
    field = q["field"]
    counts = {}
    more_results = True
    try:
        for n in hits[q.start:q.end]:
            key = get_word_attrib(n, field, db)
            if not key:
                # NULL is a magic value for queries, don't change it
                # recklessly.
                key = "NULL"
            if key not in counts:
                counts[key] = 0
            counts[key] += 1
    except IndexError:
        more_results = False

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

    word_frequency_object = {
        "results": table,
        "results_length": len(
            hits),
        "more_results": more_results
    }

    return field, word_frequency_object


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
    field, word_frequency_object = generate_word_frequency(
        hits, request, db, config)
    yield json.dumps(word_frequency_object, indent=2)


if __name__ == "__main__":
    CGIHandler().run(get_frequency)
