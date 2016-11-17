#!/usr/bin/env python

import os
from wsgiref.handlers import CGIHandler

import simplejson

import sys
sys.path.append("..")
import custom_functions

try:
    from custom_functions import generate_toc_object
except ImportError:
    from philologic.runtime import generate_toc_object
try:
    from custom_functions import WebConfig
except ImportError:
    from philologic.runtime import WebConfig
try:
    from custom_functions import WSGIHandler
except ImportError:
    from philologic.runtime import WSGIHandler


def table_of_contents(environ,start_response):
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace('reports', ''))
    request = WSGIHandler(environ, config)

    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response('200 OK',headers)
    toc_object = generate_toc_object(request, config)
    yield simplejson.dumps(toc_object)

if __name__ == "__main__":
    CGIHandler().run(table_of_contents)
