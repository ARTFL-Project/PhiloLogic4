#!/usr/bin/env python

import os
import sys
sys.path.append('..')
from philologic.DB import DB
from functions.wsgi_handler import WSGIHandler
from wsgiref.handlers import CGIHandler
from philologic.HitWrapper import ObjectWrapper
import reports as r
import functions as f
import json

def get_table_of_contents(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    path = config.db_path
    obj = ObjectWrapper(request['philo_id'].split(), db)
    toc_object = r.generate_toc_object(obj, db, request, config)
    current_obj_position = 0
    for pos, toc_element in enumerate(toc_object['toc']):
        if toc_element['philo_id'] == request.philo_id:
            toc_element['current'] = "current-obj"
            current_obj_position = pos
            break
    toc_object['current_obj_position'] = current_obj_position
    yield json.dumps(toc_object)
    
if __name__ == "__main__":
    CGIHandler().run(get_table_of_contents)