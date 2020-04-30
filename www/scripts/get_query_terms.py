#!/usr/bin/env python3

import rapidjson
import os
from wsgiref.handlers import CGIHandler

from philologic.runtime.DB import DB
from philologic.runtime.Query import get_expanded_query

import sys

sys.path.append("..")
import custom_functions

try:
    from custom_functions import WebConfig
except ImportError:
    from philologic.runtime import WebConfig
try:
    from custom_functions import WSGIHandler
except ImportError:
    from philologic.runtime import WSGIHandler


def term_list(environ, start_response):
    status = "200 OK"
    headers = [("Content-type", "application/json; charset=UTF-8"), ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace("scripts", ""))
    db = DB(config.db_path + "/data/")
    request = WSGIHandler(environ, config)
    hits = db.query(request["q"], request["method"], request["arg"], **request.metadata)
    hits.finish()
    expanded_terms = get_expanded_query(hits)
    yield rapidjson.dumps(expanded_terms[0]).encode("utf8")


if __name__ == "__main__":
    CGIHandler().run(term_list)
