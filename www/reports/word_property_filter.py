#!/usr/bin/env python

import os
from wsgiref.handlers import CGIHandler

import simplejson
from philologic.app import filter_words_by_property

from philologic.app import WebConfig
from philologic.app import WSGIHandler


def word_property_filter(environ, start_response):
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace('reports', ''))
    request = WSGIHandler(environ, config)
    headers = [('Content-type', 'application/json; charset=UTF-8'),
               ("Access-Control-Allow-Origin", "*")]
    start_response('200 OK', headers)
    filter_results = filter_words_by_property(hits, config.db_path, request,
                                              db, config)
    yield json.dumps(filter_results)


if __name__ == "__main__":
    CGIHandler().run(word_property_filter)
