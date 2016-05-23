#!/usr/bin/env python

import os
from wsgiref.handlers import CGIHandler

import simplejson
from philologic.DB import DB
from philologic.Query import get_expanded_query

from philologic.app import WebConfig
from philologic.app import WSGIHandler


def term_list(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),
               ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace('scripts', ''))
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(environ, config)
    hits = db.query(request["q"], request["method"], request["arg"],
                    **request.metadata)
    hits.finish()
    expanded_terms = get_expanded_query(hits)
    yield simplejson.dumps(expanded_terms[0])


if __name__ == "__main__":
    CGIHandler().run(term_list)
