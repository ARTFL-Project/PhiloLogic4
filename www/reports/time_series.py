#!/usr/bin/env python

import os
from wsgiref.handlers import CGIHandler

import simplejson
from philologic.app import generate_time_series

from philologic.app import WebConfig
from philologic.app import WSGIHandler


def time_series(environ, start_response):
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace('reports', ''))
    request = WSGIHandler(environ, config)
    time_series_object = generate_time_series(request, config)
    headers = [('Content-type', 'application/json; charset=UTF-8'), ("Access-Control-Allow-Origin", "*")]
    start_response('200 OK', headers)
    yield simplejson.dumps(time_series_object)




if __name__ == '__main__':
    CGIHandler().run(time_series)
