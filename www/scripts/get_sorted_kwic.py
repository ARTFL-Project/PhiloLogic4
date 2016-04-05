#!/usr/bin/env python

import sys
from wsgiref.handlers import CGIHandler

from philologic.DB import DB

sys.path.append('..')
import functions as f
import reports as r
from functions.wsgi_handler import WSGIHandler

try:
    import ujson as json
except ImportError:
    import json


def get_sorted_kwic(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),
               ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    input_object = json.loads(environ['wsgi.input'].read())
    indices = input_object['results']
    query_string = input_object['query_string']
    environ['QUERY_STRING'] = query_string.encode('utf8')
    request = WSGIHandler(db, environ)
    sorted_hits = get_sorted_hits(indices, request, config, db,
                                  input_object['start'], input_object['end'])
    yield json.dumps(sorted_hits)


def get_sorted_hits(indices, q, config, db, start, end):
    hits = db.query(q["q"], q["method"], q["arg"], **q.metadata)
    start, end, n = f.link.page_interval(q.results_per_page, hits, start, end)
    kwic_object = {
        "description":
        {"start": start,
         "end": end,
         "results_per_page": q.results_per_page},
        "query": dict([i for i in q])
    }

    kwic_results = []

    for index in indices:
        hit = hits[index[1]]
        kwic_result = r.kwic_hit_object(hit, config, db)
        kwic_results.append(kwic_result)

    kwic_object['results'] = kwic_results
    kwic_object['results_length'] = len(hits)
    kwic_object["query_done"] = hits.done

    return kwic_object


if __name__ == "__main__":
    CGIHandler().run(get_sorted_kwic)
