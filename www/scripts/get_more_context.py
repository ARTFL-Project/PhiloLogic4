#!/usr/bin/env python

import sys
from philologic.DB import DB
sys.path.append('..')
from functions.wsgi_handler import WSGIHandler
from wsgiref.handlers import CGIHandler
import reports as r
import functions as f
import json

def get_more_context(environ,start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    hit_num = int(request.hit_num)
    hits = db.query(request["q"],request["method"],request["arg"],**request.metadata)
    context_size = config['concordance_length'] * 3
    hit_context = r.fetch_concordance(db, hits[hit_num], config.db_path, context_size)
    yield json.dumps(hit_context)

if __name__ == "__main__":
    CGIHandler().run(get_more_context)
