#!/usr/bin/env python

import os
from wsgiref.handlers import CGIHandler

from philologic.app import WebConfig


def get_web_config(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),
               ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace('scripts', '')).to_json()
    yield config


if __name__ == "__main__":
    CGIHandler().run(get_web_config)
