#!/usr/bin/env python3

import json
import os
from wsgiref.handlers import CGIHandler

from philologic.runtime import WebConfig, WSGIHandler, generate_toc_object


def get_table_of_contents(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),
               ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace('scripts', ''))
    request = WSGIHandler(environ, config)
    philo_id = request['philo_id'].split()
    toc_object = generate_toc_object(request, config)
    current_obj_position = 0
    philo_id = ' '.join(philo_id)
    for pos, toc_element in enumerate(toc_object['toc']):
        if toc_element['philo_id'] == philo_id:
            current_obj_position = pos
            break
    toc_object['current_obj_position'] = current_obj_position
    yield json.dumps(toc_object).encode('utf8')


if __name__ == "__main__":
    CGIHandler().run(get_table_of_contents)
