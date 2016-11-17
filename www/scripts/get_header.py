#!/usr/bin/env python

import os
from wsgiref.handlers import CGIHandler

from philologic.runtime import get_tei_header

from philologic.runtime import WebConfig
from philologic.runtime import WSGIHandler


def get_header(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=UTF-8'),
               ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace('scripts', ''))
    request = WSGIHandler(environ, config)
    header = get_tei_header(request, config)
    yield header


if __name__ == "__main__":
    CGIHandler().run(get_header)
