#!/usr/bin/env python3

import os
from wsgiref.handlers import CGIHandler

import rapidjson

import sys

sys.path.append("..")
import custom_functions

try:
    from custom_functions import aggregation_by_field
except ImportError:
    from philologic.runtime import aggregation_by_field
try:
    from custom_functions import WebConfig
except ImportError:
    from philologic.runtime import WebConfig
try:
    from custom_functions import WSGIHandler
except ImportError:
    from philologic.runtime import WSGIHandler


def aggregation(environ, start_response):
    config = WebConfig(
        os.path.abspath(os.path.dirname(__file__)).replace("reports", "")
    )
    request = WSGIHandler(environ, config)
    aggregation_object = aggregation_by_field(request, config)
    headers = [
        ("Content-type", "application/json; charset=UTF-8"),
        ("Access-Control-Allow-Origin", "*"),
    ]
    start_response("200 OK", headers)
    yield rapidjson.dumps(aggregation_object).encode("utf8")


if __name__ == "__main__":
    CGIHandler().run(aggregation)
