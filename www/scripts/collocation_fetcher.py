#!/usr/bin/env python

import os
import sys
sys.path.append('..')
from functions.wsgi_handler import parse_cgi
from wsgiref.handlers import CGIHandler
import reports as r
import cgi
from json import dumps

def collocation_fetcher(environ,start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    environ["SCRIPT_FILENAME"] = environ["SCRIPT_FILENAME"].replace('scripts/collocation_fetcher.py', '')
    db, path_components, q = parse_cgi(environ)
    hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
    all_colloc, left_colloc, right_colloc = r.fetch_collocation(hits, environ["SCRIPT_FILENAME"], q, db)
    yield dumps([all_colloc, left_colloc, right_colloc])
    
if __name__ == "__main__":
    CGIHandler().run(collocation_fetcher)
