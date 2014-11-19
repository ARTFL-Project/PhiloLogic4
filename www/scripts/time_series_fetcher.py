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
import json

def time_series_fetcher(environ,start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    request = r.handle_dates(request, db)
    results = db.query(request["q"],request["method"],request["arg"],**request.metadata)
    time_series_object = r.generate_time_series(request, db, results)
    yield json.dumps(time_series_object)

if __name__ == "__main__":
    CGIHandler().run(time_series_fetcher)
