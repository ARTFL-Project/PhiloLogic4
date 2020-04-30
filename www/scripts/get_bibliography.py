#!/usr/bin/env python3

import rapidjson
import os
from wsgiref.handlers import CGIHandler

from philologic5.runtime import landing_page_bibliography

import sys

sys.path.append("..")
import custom_functions

try:
    from custom_functions import WebConfig
except ImportError:
    from philologic5.runtime import WebConfig
try:
    from custom_functions import WSGIHandler
except ImportError:
    from philologic5.runtime import WSGIHandler


def get_bibliography(environ, start_response):
    status = "200 OK"
    headers = [("Content-type", "application/json; charset=UTF-8"), ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace("scripts", ""))
    request = WSGIHandler(environ, config)
    results = landing_page_bibliography(request, config)
    yield rapidjson.dumps(results).encode("utf8")


if __name__ == "__main__":
    CGIHandler().run(get_bibliography)
