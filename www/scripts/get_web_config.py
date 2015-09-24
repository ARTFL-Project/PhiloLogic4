#!/usr/bin/env python

import sys
sys.path.append('..')
import functions as f
from wsgiref.handlers import CGIHandler


def get_web_config(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),
               ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = f.WebConfig().to_json()
    yield config


if __name__ == "__main__":
    CGIHandler().run(get_web_config)
