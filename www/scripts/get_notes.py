#!/usr/bin/env python

import os
from wsgiref.handlers import CGIHandler

import simplejson
from philologic.app import generate_text_object
from philologic.DB import DB
from philologic.HitWrapper import ObjectWrapper

from philologic.app import WebConfig
from philologic.app import WSGIHandler


def get_notes(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),
               ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace('scripts', ''))
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(environ, config)
    text_object = generate_text_object(request, config, note=True)
    yield simplejson.dumps(text_object)


if __name__ == "__main__":
    CGIHandler().run(get_notes)
