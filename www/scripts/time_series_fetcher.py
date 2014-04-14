#!/usr/bin/env python

import os
import sys
import urlparse
sys.path.append('..')
from functions.wsgi_handler import parse_cgi
from wsgiref.handlers import CGIHandler
import reports as r
import json

def time_series_fetcher(environ,start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    environ["SCRIPT_FILENAME"] = environ["SCRIPT_FILENAME"].replace('scripts/time_series_fetcher.py', '')
    cgi = urlparse.parse_qs(environ["QUERY_STRING"],keep_blank_values=True)
    db, path_components, q = parse_cgi(environ)
    if q['start_date']:
        q['metadata']['date'] = '%s-' % q['start_date']
    if q['end_date']:
        if 'date' in q['metadata']:
            q['metadata']['date']+= '%s' % q['end_date']
        else:
            q['metadata']['date'] = '-%s' % q['end_date']
    results = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
    absolute_frequency, date_counts = r.generate_time_series(q, db, results)
    yield json.dumps([json.loads(absolute_frequency), json.loads(date_counts)])

if __name__ == "__main__":
    CGIHandler().run(time_series_fetcher)
