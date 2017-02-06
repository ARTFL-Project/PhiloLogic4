#!/usr/bin/env python

import os
from wsgiref.handlers import CGIHandler

import simplejson
from philologic.runtime import frequency_results

from philologic.runtime import WebConfig
from philologic.runtime import WSGIHandler


def get_frequency(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),
               ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace('scripts', ''))
    request = WSGIHandler(environ, config)
    results = frequency_results(request, config, sorted_results=True)
    yield simplejson.dumps(results)


if __name__ == "__main__":
    CGIHandler().run(get_frequency)
