#!/usr/bin/env python

import os
import sys
from wsgiref.handlers import CGIHandler

import simplejson
from philologic.runtime import get_concordance_text
from philologic.DB import DB

from philologic.runtime import WebConfig
from philologic.runtime import WSGIHandler


def get_more_context(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),
               ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace('scripts', ''))
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(environ, config)
    hit_num = int(request.hit_num)
    hits = db.query(request["q"], request["method"], request["arg"],
                    **request.metadata)
    context_size = config['concordance_length'] * 3
    hit_context = get_concordance_text(db, hits[hit_num], config.db_path,
                                       context_size)
    yield simplejson.dumps(hit_context)


if __name__ == "__main__":
    CGIHandler().run(get_more_context)
