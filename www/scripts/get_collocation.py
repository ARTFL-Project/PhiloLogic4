#!/usr/bin/env python

import os
import sys
import urlparse
sys.path.append('..')
from functions.wsgi_handler import parse_cgi
from wsgiref.handlers import CGIHandler
import reports as r
import functions as f
import cgi
from json import dumps
from ast import literal_eval as eval

def collocation_fetcher(environ,start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    environ["SCRIPT_FILENAME"] = environ["SCRIPT_FILENAME"].replace('scripts/get_collocation.py', '')
    cgi = urlparse.parse_qs(environ["QUERY_STRING"],keep_blank_values=True)
    report_type = cgi.get('collocation_type',['full'])[0]
    db, path_components, q = parse_cgi(environ)
    hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
    config = f.WebConfig()
    collocation_object = r.fetch_collocation(hits, environ["SCRIPT_FILENAME"], q, db, config)
    yield dumps(collocation_object)

if __name__ == "__main__":
    CGIHandler().run(collocation_fetcher)
