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
    if request.start == 0:
        start = 0
    else:
        start = request.start - 1
    end = (request.end or request.results_per_page) + 1
    hit_range = range(start, end)
    hits = db.query(request["q"],request["method"],request["arg"],**request.metadata)
    context_size = config['concordance_length'] * 3
    html_list = []
    for i in hit_range:
        try:
            html_list.append(r.fetch_concordance(db, hits[i], config.db_path, context_size))
        except IndexError:
            break
    yield json.dumps(html_list)

if __name__ == "__main__":
    CGIHandler().run(get_more_context)
