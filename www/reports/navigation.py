#!/usr/bin/env python3

import os
from wsgiref.handlers import CGIHandler

import json

import sys
sys.path.append("..")
import custom_functions

try:
    from custom_functions import generate_text_object
except ImportError:
    from philologic.runtime import generate_text_object
try:
    from custom_functions import WebConfig
except ImportError:
    from philologic.runtime import WebConfig
try:
    from custom_functions import WSGIHandler
except ImportError:
    from philologic.runtime import WSGIHandler


def navigation(environ, start_response):
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace('reports', ''))
    request = WSGIHandler(environ, config)
    headers = [('Content-type', 'application/json; charset=UTF-8'),
               ("Access-Control-Allow-Origin", "*")]
    start_response('200 OK', headers)
    text_object = generate_text_object(request, config)
    yield json.dumps(text_object).encode('utf8')


if __name__ == "__main__":
    CGIHandler().run(navigation)
