#!/usr/bin/env python

import os
import sys
import urlparse
sys.path.append('..')
from functions.wsgi_handler import WSGIHandler
from philologic.DB import DB
from wsgiref.handlers import CGIHandler
import reports as r
import functions as f
import cgi
import json
import sqlite3
import time

def get_frequency(environ,start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    if request.q == '' and request.no_q:
        hits = db.get_all(db.locals['default_object_level'])
    else:
        hits = db.query(request["q"],request["method"],request["arg"],**request.metadata)
    field, results = r.generate_frequency(hits, request, db, config)
    yield json.dumps(results)
    

if __name__ == "__main__":
    CGIHandler().run(get_frequency)
