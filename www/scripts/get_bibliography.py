#!/usr/bin/env python

import os
import sys
import urlparse
sys.path.append('..')
from functions.wsgi_handler import parse_cgi
from wsgiref.handlers import CGIHandler
import reports as r
import cgi
import json

object_levels = set(["doc", "div1", "div2", "div3"])

def get_bibliography(environ,start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    environ["SCRIPT_FILENAME"] = environ["SCRIPT_FILENAME"].replace('scripts/get_bibliography.py', '')
    cgi = urlparse.parse_qs(environ["QUERY_STRING"],keep_blank_values=True)
    object_level = cgi.get('object_level', '')[0]
    db, path_components, q = parse_cgi(environ)
    if object_level and object_level in object_levels:
        hits = db.get_all(object_level)
    else:
        hits = db.get_all(db.locals['default_object_level'])
    
    results = []
    for hit in hits:
        hit_object = {}
        for field in db.locals['metadata_fields']:
            hit_object[field] = hit[field] or ''
        hit_object['philo_id'] = hit.philo_id
        results.append(hit_object)
    
    yield json.dumps(results)

if __name__ == "__main__":
    CGIHandler().run(get_bibliography)