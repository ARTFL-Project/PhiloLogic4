#!/usr/bin/env python

import os
from wsgiref.handlers import CGIHandler

import simplejson
from philologic.app import generate_toc_object
from philologic.DB import DB
from philologic.HitWrapper import ObjectWrapper

from philologic.app import WebConfig
from philologic.app import WSGIHandler


def get_table_of_contents(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),
               ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace('scripts', ''))
    request = WSGIHandler(environ, config)
    philo_id = request['philo_id'].split()
    # obj = ObjectWrapper(philo_id, db)
    # while obj.philo_name == '__philo_virtual' and obj.philo_type != "div1":
    #     philo_id.pop()
    #     obj = ObjectWrapper(philo_id, db)
    toc_object = generate_toc_object(request, config)
    current_obj_position = 0
    philo_id = ' '.join(philo_id)
    for pos, toc_element in enumerate(toc_object['toc']):
        if toc_element['philo_id'] == philo_id:
            current_obj_position = pos
            break
    toc_object['current_obj_position'] = current_obj_position
    yield simplejson.dumps(toc_object)


if __name__ == "__main__":
    CGIHandler().run(get_table_of_contents)
