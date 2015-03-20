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
import cgi
import json

object_levels = set(["doc", "div1", "div2", "div3"])

def get_bibliography(environ,start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    object_level = request.object_level
    if object_level and object_level in object_levels:
        hits = db.get_all(object_level)
    else:
        hits = db.get_all(db.locals['default_object_level'])
    results = []
    for hit in hits:
        hit_object = {}
        for field in db.locals['metadata_fields']:
            hit_object[field] = hit[field] or ''
        if object_level == "doc":
            hit_object['philo_id'] = hit.philo_id[0]
        else:
            hit_object['philo_id'] = '/'.join([str(i) for i in hit.philo_id])
        results.append(hit_object)
    
    yield json.dumps(results)

if __name__ == "__main__":
    CGIHandler().run(get_bibliography)