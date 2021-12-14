#!/usr/bin/env python3

import orjson
import os
from wsgiref.handlers import CGIHandler

from philologic.runtime import frequency_results

import sys

sys.path.append("..")
import custom_functions

try:
    from custom_functions import WebConfig
except ImportError:
    from philologic.runtime import WebConfig
try:
    from custom_functions import WSGIHandler
except ImportError:
    from philologic.runtime import WSGIHandler


def get_frequency(environ, start_response):
    """reads through a hitlist. looks up q.frequency_field in each hit, and builds up a list of
    unique values and their frequencies."""
    status = "200 OK"
    headers = [("Content-type", "application/json; charset=UTF-8"), ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace("scripts", ""))
    request = WSGIHandler(environ, config)
    results = frequency_results(request, config, sorted_results=True)
    yield orjson.dumps(results)


if __name__ == "__main__":
    CGIHandler().run(get_frequency)
