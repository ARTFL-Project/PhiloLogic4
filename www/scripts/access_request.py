#! /usr/bin/env python

import sys
sys.path.append('..')
import functions as f
from functions.wsgi_handler import WSGIHandler
from philologic.DB import DB
from wsgiref.handlers import CGIHandler
from ast import literal_eval as eval
import json


default_reports = ['concordance', 'kwic', 'collocation', 'time_series', 'navigation']


def access_request(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'), ("Access-Control-Allow-Origin", "*")]
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    access, headers = f.login_access(environ, config, db, headers)
    start_response(status, headers)
    if access:
        yield json.dumps({'access': True})
    else:
        yield json.dumps({'access': False})

if __name__ == "__main__":
    CGIHandler().run(access_request)
