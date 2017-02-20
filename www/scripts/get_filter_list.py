#!/usr/bin/env python3

import json
import os
from wsgiref.handlers import CGIHandler

from philologic.runtime import WebConfig, WSGIHandler, build_filter_list


def get_filter_list(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),
               ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace('scripts', ''))
    request = WSGIHandler(environ, config)
    filter_list = build_filter_list(request, config)
    yield json.dumps(filter_list).encode('utf8')


if __name__ == "__main__":
    CGIHandler().run(get_filter_list)
