#!/usr/bin/env python3

import json
import os
from wsgiref.handlers import CGIHandler

from philologic.DB import DB
from philologic.runtime import generate_text_object

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


def get_notes(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),
               ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace('scripts', ''))
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(environ, config)
    text_object = generate_text_object(request, config, note=True)
    yield json.dumps(text_object).encode('utf8')


if __name__ == "__main__":
    CGIHandler().run(get_notes)
