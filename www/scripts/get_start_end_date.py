#!/usr/bin/env python

import sys
sys.path.append('..')
from wsgiref.handlers import CGIHandler
from philologic.DB import DB
from functions.wsgi_handler import WSGIHandler
import functions as f
import reports as r
import json


def get_start_end_date(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=UTF-8'),
               ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    start_date, end_date = r.get_start_end_date(
        db,
        start_date=request.start_date,
        end_date=request.end_date)
    yield json.dumps({"start_date": start_date, "end_date": end_date})


if __name__ == "__main__":
    CGIHandler().run(get_start_end_date)
