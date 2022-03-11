#!/usr/bin/env python3

import os
from wsgiref.handlers import CGIHandler

from philologic.runtime import group_by_metadata, group_by_range

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


def landing_page_content(environ, start_response):
    """Get landing page content"""
    status = "200 OK"
    headers = [("Content-type", "application/json; charset=UTF-8"), ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace("scripts", ""))
    request = WSGIHandler(environ, config)
    if request.is_range == "true":
        if isinstance(request.query, bytes):
            request_range = request.query.decode("utf8")
        request_range = [item.strip() for item in request.query.lower().split("-")]
        if len(request_range) == 1:
            request_range.append(request_range[0])
        results = group_by_range(request_range, request, config)
    else:
        results = group_by_metadata(request, config)
    yield results


if __name__ == "__main__":
    CGIHandler().run(landing_page_content)
