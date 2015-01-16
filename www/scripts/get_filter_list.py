#!/usr/bin/env python

import os
import sys
from philologic.DB import DB
sys.path.append('..')
from functions.wsgi_handler import WSGIHandler
from wsgiref.handlers import CGIHandler
import reports as r
import functions as f
import json

def get_filter_list(environ,start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    filter_list = r.collocation.build_filter_list(request, config)
    yield json.dumps(filter_list)

if __name__ == "__main__":
    CGIHandler().run(get_filter_list)
