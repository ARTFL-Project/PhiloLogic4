#!/usr/bin/env python3

import json
import os
from wsgiref.handlers import CGIHandler

from philologic.runtime import WebConfig, WSGIHandler, concordance_results


def get_frequency(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),
               ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace('scripts', ''))
    request = WSGIHandler(environ, config)
    word_frequency_object = generate_word_frequency(request, config)
    yield json.dumps(word_frequency_object).encode('utf8')


if __name__ == "__main__":
    CGIHandler().run(get_frequency)
