#!/usr/bin/env python

import os
import sys
sys.path.append('..')
from philologic.DB import DB
from functions.wsgi_handler import WSGIHandler
from wsgiref.handlers import CGIHandler
from philologic.HitWrapper import ObjectWrapper
import functions as f
from reports.navigation import generate_text_object
try:
    import ujson as json
except ImportError:
    import json

def get_text_object(environ,start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)    
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    path = config.db_path
    zeros = 7 - len(request.philo_id)
    if zeros:
        request.philo_id += zeros * " 0"
    print >> sys.stderr, "REQUEST", request['philo_id'].split()
    obj = ObjectWrapper(request['philo_id'].split(), db)
    text_object = generate_text_object(obj, db, request, config)
    yield json.dumps(text_object)

if __name__ == "__main__":
    CGIHandler().run(get_text_object)
