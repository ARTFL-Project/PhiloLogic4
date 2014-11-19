#!/usr/bin/env python

import os
import sys
import urlparse
sys.path.append('..')
from functions.wsgi_handler import WSGIHandler
from wsgiref.handlers import CGIHandler
from philologic.DB import DB
import reports as r
import functions as f
import json

def get_total_results(environ,start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    environ["SCRIPT_FILENAME"] = environ["SCRIPT_FILENAME"].replace('scripts/get_total_results.py', '')
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    if request.no_q:
        hits = db.get_all(db.locals['default_object_level'])
    else:
        hits = db.query(request["q"],request["method"],request["arg"],**request.metadata)
    total_results = 0
    while total_results == 0:
        if hits.done:
            break
    total_results = len(hits)
        
    yield json.dumps(total_results)

if __name__ == "__main__":
    CGIHandler().run(get_total_results)
