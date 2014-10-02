#!/usr/bin/env python

import os
import sys
import urlparse
sys.path.append('..')
from functions.wsgi_handler import parse_cgi
from wsgiref.handlers import CGIHandler
import reports as r
import cgi
import json

def get_frequency(environ,start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    environ["SCRIPT_FILENAME"] = environ["SCRIPT_FILENAME"].replace('scripts/get_frequency.py', '')
    cgi = urlparse.parse_qs(environ["QUERY_STRING"],keep_blank_values=True)
    frequency_field = cgi.get('frequency_field',[''])[0]
    db, path_components, q = parse_cgi(environ)
    q['field'] = frequency_field
    if q['q'] == '' and q["no_q"]:
        hits = db.get_all(db.locals['default_object_level'])
    else:
        hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
    if q["format"] == "json":
        while not len(hits):
            time.sleep(0.5) ## this should be enough time to write all results to disk in most instances.... better fix later
        q["interval_start"] = 0
        q["interval_end"] = len(hits)
        bib_values = dict([(i, j) for i, j in q['metadata'].iteritems() if j])
        field, results = r.generate_frequency(hits, q, db)
        new_results = []
        for label, result in sorted(results.iteritems(), key=lambda (x, y): y["count"], reverse=True):
            formatted_result = {"search_term": q['q'], "frequency_field": frequency_field, "results": label, "count": result["count"], "url": "dispatcher.py/" + result["url"].replace('./', ''),
                                "bib_values": bib_values}
            new_results.append(formatted_result)
        yield json.dumps(new_results)
    else:
        field, results = r.generate_frequency(hits, q, db)
        yield json.dumps(results,indent=2)

if __name__ == "__main__":
    CGIHandler().run(get_frequency)
