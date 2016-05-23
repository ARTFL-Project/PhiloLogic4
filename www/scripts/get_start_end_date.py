#!/usr/bin/env python

import os
from wsgiref.handlers import CGIHandler

import simplejson
from philologic.app import get_start_end_date as start_end_date
from philologic.DB import DB

from philologic.app import WebConfig
from philologic.app import WSGIHandler


def get_start_end_date(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=UTF-8'), ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace('scripts', ''))
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(environ, config)
    start_date, end_date = start_end_date(db, start_date=request.start_date, end_date=request.end_date)
    yield simplejson.dumps({"start_date": start_date, "end_date": end_date})


if __name__ == "__main__":
    CGIHandler().run(get_start_end_date)
