#!/usr/bin/env python3

import json
import os
from wsgiref.handlers import CGIHandler

from philologic.DB import DB
from philologic.runtime import get_start_end_date as start_end_date

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


def get_start_end_date(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=UTF-8'), ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace('scripts', ''))
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(environ, config)
    start_date, end_date = start_end_date(db, config, start_date=request.start_date, end_date=request.end_date)
    yield json.dumps({"start_date": start_date, "end_date": end_date}).encode('utf8')


if __name__ == "__main__":
    CGIHandler().run(get_start_end_date)
