#!/usr/bin/env python

import os
from wsgiref.handlers import CGIHandler

import simplejson
from philologic.DB import DB

from philologic.runtime.link import byte_range_to_link
from philologic.runtime import WebConfig
from philologic.runtime import WSGIHandler


def alignment_to_text(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),
               ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace('scripts', ''))
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(environ, config)
    link = byte_range_to_link(db, config, request)
    yield simplejson.dumps({"link": link})

if __name__ == '__main__':
    CGIHandler().run(alignment_to_text)