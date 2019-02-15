#!/usr/bin/env python3

import json
import os
from wsgiref.handlers import CGIHandler

from philologic.runtime.DB import DB

import sys
sys.path.append("..")
import custom_functions
try:
     from custom_functions import WebConfig
except ImportError:
     from philologic.runtime import WebConfig
try:
     from custom_functions import WSGIHandler
except ImportError:
     from philologic.runtime import WSGIHandler


def get_total_results(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),
               ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace('scripts', ''))
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(environ, config)
    if request.no_q:
        if request.no_metadata:
            hits = db.get_all(db.locals['default_object_level'], request["sort_order"])
        else:
            hits = db.query(sort_order=request["sort_order"], **request.metadata)
    else:
        hits = db.query(request["q"], request["method"], request["arg"],
                        **request.metadata)
    total_results = 0
    hits.finish()
    total_results = len(hits)

    yield json.dumps(total_results).encode('utf8')


if __name__ == "__main__":
    CGIHandler().run(get_total_results)
