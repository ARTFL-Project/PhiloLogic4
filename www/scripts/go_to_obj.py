#!/usr/bin/env python

import os
import sys
sys.path.append('..')
from functions.wsgi_handler import parse_cgi
from wsgiref.handlers import CGIHandler
from philologic.HitWrapper import ObjectWrapper
import functions as f
import json

def go_to_obj(environ,start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)    
    environ["SCRIPT_FILENAME"] = environ["SCRIPT_FILENAME"].replace('scripts/go_to_obj.py', '')
    db, path_components, q = parse_cgi(environ)
    path = db.locals['db_path']
    path = path[:path.rfind("/data")]
    philo_obj = ObjectWrapper(q['philo_id'].split(), db)
    prev_obj = ' '.join(philo_obj.prev.split()[:7])
    next_obj = ' '.join(philo_obj.next.split()[:7])
    text = f.get_text_obj(philo_obj, path)
    yield json.dumps({'text': text, "prev": prev_obj, "next": next_obj})

if __name__ == "__main__":
    CGIHandler().run(go_to_obj)
