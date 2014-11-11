#!/usr/bin/env python

import os
import sys
sys.path.append('..')
from functions.wsgi_handler import parse_cgi
from wsgiref.handlers import CGIHandler
from philologic.HitWrapper import ObjectWrapper
from mako.template import Template
import reports as r
import functions as f
import json

obj_level = {'doc': 1, 'div1': 2, 'div2': 3, 'div3': 4}

def get_table_of_contents(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    environ["SCRIPT_FILENAME"] = environ["SCRIPT_FILENAME"].replace('scripts/get_table_of_contents.py', '')
    db, path_components, q = parse_cgi(environ)
    config = f.WebConfig()
    path = db.locals['db_path']
    path = path[:path.rfind("/data")]
    obj = ObjectWrapper(q['philo_id'].split(), db)
    toc_object = r.generate_toc_object(obj, db, q, config)
    yield json.dumps(toc_object)
    
if __name__ == "__main__":
    CGIHandler().run(get_table_of_contents)