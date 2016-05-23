#!/usr/bin/env python

import os
import re
import sys
import unicodedata
from wsgiref.handlers import CGIHandler

import simplejson
from philologic.app import group_by_metadata, group_by_range

from philologic.app import WebConfig
from philologic.app import WSGIHandler

object_depth = {"doc": 1, "div1": 2, "div2": 3, "div3": 4, "para": 5}


def landing_page_content(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),
               ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace('scripts', ''))
    request = WSGIHandler(environ, config)
    if request.is_range == 'true':
        if type(request.query) == str:
            request_range = request.query.decode("utf8")
        request_range = request_range.lower().split('-')
        results = group_by_range(request_range, request, config)
    else:
        results = group_by_metadata(request)
    yield results


if __name__ == "__main__":
    CGIHandler().run(landing_page_content)
