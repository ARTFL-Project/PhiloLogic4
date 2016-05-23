#!/usr/bin/env python

import os
from wsgiref.handlers import CGIHandler

import simplejson
from philologic.app import generate_text_object

from philologic.app import WebConfig
from philologic.app import WSGIHandler


def navigation(environ, start_response):
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace('reports', ''))
    request = WSGIHandler(environ, config)
    headers = [('Content-type', 'application/json; charset=UTF-8'),
               ("Access-Control-Allow-Origin", "*")]
    start_response('200 OK', headers)
    text_object = generate_text_object(request, config)
    yield simplejson.dumps(text_object)


if __name__ == "__main__":
    CGIHandler().run(navigation)
