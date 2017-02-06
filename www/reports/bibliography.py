#!/usr/bin/env python33

import os
from wsgiref.handlers import CGIHandler

import json

import sys
sys.path.append("..")
import custom_functions

try:
    from custom_functions import bibliography_results
except ImportError:
    from philologic.runtime import bibliography_results
try:
    from custom_functions import WebConfig
except ImportError:
    from philologic.runtime import WebConfig
try:
    from custom_functions import WSGIHandler
except ImportError:
    from philologic.runtime import WSGIHandler


def bibliography(environ, start_response):
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace('reports', ''))
    request = WSGIHandler(environ, config)
    headers = [('Content-type', 'application/json; charset=UTF-8'),
               ("Access-Control-Allow-Origin", "*")]
    start_response('200 OK', headers)
    bibliography_object, hits = bibliography_results(request, config)
    yield json.dumps(bibliography_object).encode('utf8')


if __name__ == "__main__":
    CGIHandler().run(bibliography)
