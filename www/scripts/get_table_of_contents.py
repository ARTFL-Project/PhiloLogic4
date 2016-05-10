#!/usr/bin/env python

import sys
sys.path.append('..')
from philologic.DB import DB
from functions.wsgi_handler import WSGIHandler
from wsgiref.handlers import CGIHandler
from philologic.HitWrapper import ObjectWrapper
import reports as r
import functions as f
try:
    import simplejson as json
except ImportError:
    import json


def get_table_of_contents(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),
               ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    philo_id = request['philo_id'].split()
    obj = ObjectWrapper(philo_id, db)
    while obj.philo_name == '__philo_virtual' and obj.philo_type != "div1":
        philo_id.pop()
        obj = ObjectWrapper(philo_id, db)
    toc_object = r.generate_toc_object(obj, db, request, config)
    current_obj_position = 0
    philo_id = ' '.join(philo_id)
    for pos, toc_element in enumerate(toc_object['toc']):
        if toc_element['philo_id'] == philo_id:
            current_obj_position = pos
            break
    toc_object['current_obj_position'] = current_obj_position
    yield json.dumps(toc_object)


if __name__ == "__main__":
    CGIHandler().run(get_table_of_contents)
