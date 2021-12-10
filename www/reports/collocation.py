#!/usr/bin/env python3

import os
from wsgiref.handlers import CGIHandler

import orjson

import sys

sys.path.append("..")
import custom_functions

try:
    from custom_functions import collocation_results
except ImportError:
    from philologic.runtime import collocation_results
try:
    from custom_functions import WebConfig
except ImportError:
    from philologic.runtime import WebConfig
try:
    from custom_functions import WSGIHandler
except ImportError:
    from philologic.runtime import WSGIHandler


def collocation(environ, start_response):
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace("reports", ""))
    request = WSGIHandler(environ, config)
    headers = [("Content-type", "application/json; charset=UTF-8"), ("Access-Control-Allow-Origin", "*")]
    start_response("200 OK", headers)
    collocation_object = collocation_results(request, config)
    yield orjson.dumps(collocation_object)


if __name__ == "__main__":
    CGIHandler().run(collocation)
