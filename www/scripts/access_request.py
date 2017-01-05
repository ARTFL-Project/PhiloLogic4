#! /usr/bin/env python

import os
from wsgiref.handlers import CGIHandler

import simplejson
from philologic.DB import DB
from philologic.runtime import WebConfig, WSGIHandler, login_access


default_reports = ['concordance', 'kwic', 'collocation', 'time_series',
                   'navigation']


def access_request(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),
               ("Access-Control-Allow-Origin", "*")]
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace('scripts', ''))
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(environ, config)
    access, headers = login_access(environ, request, config, headers)
    start_response(status, headers)
    if access:
        yield simplejson.dumps({'access': True})
    else:
        yield simplejson.dumps({'access': False})


if __name__ == "__main__":
    CGIHandler().run(access_request)
