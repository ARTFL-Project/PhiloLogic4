#!/usr/bin/env python3

import json
import os
from wsgiref.handlers import CGIHandler

from philologic.runtime import (WebConfig, WSGIHandler,
                                landing_page_bibliography)


def get_bibliography(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),
               ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace('scripts', ''))
    request = WSGIHandler(environ, config)
    results = landing_page_bibliography(request, config)
    yield json.dumps(results).encode('utf8')


if __name__ == "__main__":
    CGIHandler().run(get_bibliography)
