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
    interval_start = int(cgi.get('interval_start',[''])[0])
    interval_end = int(cgi.get('interval_end',[''])[0])
    db, path_components, q = parse_cgi(environ)
    q['field'] = frequency_field
    if q['q'] == '' and q["no_q"]:
        hits = db.get_all(db.locals['default_object_level'])
    else:
        hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
    field, results = r.generate_frequency(hits, q, db, interval_start, interval_end)
    yield json.dumps(results,indent=2)

if __name__ == "__main__":
    CGIHandler().run(get_frequency)
