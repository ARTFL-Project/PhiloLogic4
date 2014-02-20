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

def get_total_results(environ,start_response):
    print >> sys.stderr, "SCRIPT FIRED"
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    environ["SCRIPT_FILENAME"] = environ["SCRIPT_FILENAME"].replace('scripts/get_total_results.py', '')
    cgi = urlparse.parse_qs(environ["QUERY_STRING"],keep_blank_values=True)
    db, path_components, q = parse_cgi(environ)
    if q['q'] == '' and q["no_q"]:
        hits = db.get_all(db.locals['default_object_level'])
    else:
        hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
    total_results = 0
    while total_results == 0:
        if hits.done:
            break
    total_results = len(hits)
        
    yield json.dumps(total_results)

if __name__ == "__main__":
    CGIHandler().run(get_total_results)
