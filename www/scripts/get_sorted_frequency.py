#!/usr/bin/env python3

import os
from ast import literal_eval as eval
from wsgiref.handlers import CGIHandler

import simplejson
from philologic.runtime import frequency_results
from philologic.DB import DB

from philologic.runtime import WebConfig
from philologic.runtime import WSGIHandler


def get_frequency(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),
               ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace('scripts', ''))
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(environ, config)
    setattr(request, 'frequency_field', simplejson.dumps(
        eval('"%s"' % request.frequency_field)))
    results = frequency_results(request, config, sorted=True)
    yield simplejson.dumps(results)


if __name__ == "__main__":
    CGIHandler().run(get_frequency)
