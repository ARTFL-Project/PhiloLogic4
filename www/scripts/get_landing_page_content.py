#!/usr/bin/env python3

import os
import re
import sys
import unicodedata
from wsgiref.handlers import CGIHandler

import json
from philologic.runtime import group_by_metadata, group_by_range

from philologic.runtime import WebConfig
from philologic.runtime import WSGIHandler

object_depth = {"doc": 1, "div1": 2, "div2": 3, "div3": 4, "para": 5}


def landing_page_content(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),
               ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace('scripts', ''))
    request = WSGIHandler(environ, config)
    if request.is_range == 'true':
        if isinstance(request.query, bytes):
            request_range = request.query.decode("utf8")
        request_range = request.query.lower().split('-')
        results = group_by_range(request_range, request, config)
    else:
        results = group_by_metadata(request, config)
    yield results.encode('utf8')


if __name__ == "__main__":
    CGIHandler().run(landing_page_content)
