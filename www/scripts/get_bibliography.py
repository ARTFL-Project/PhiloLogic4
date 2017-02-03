#!/usr/bin/env python3

import os
import sqlite3
from wsgiref.handlers import CGIHandler

import json
from philologic.DB import DB

from philologic.runtime import landing_page_bibliography
from philologic.runtime import WebConfig
from philologic.runtime import WSGIHandler


def get_bibliography(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),
               ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace('scripts', ''))
    request = WSGIHandler(environ, config)
    results = landing_page_bibliography(request, config)
    yield json.dumps(results)


if __name__ == "__main__":
    CGIHandler().run(get_bibliography)
