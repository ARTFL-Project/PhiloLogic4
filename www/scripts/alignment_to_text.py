#!/usr/bin/env python3

import os
import sys
from json import dumps
from wsgiref.handlers import CGIHandler

from philologic.runtime.DB import DB
from philologic.runtime.link import byte_range_to_link

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


def alignment_to_text(environ, start_response):
    status = "200 OK"
    headers = [("Content-type", "application/json; charset=UTF-8"), ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace("scripts", ""))
    db = DB(config.db_path + "/data/")
    request = WSGIHandler(environ, config)
    link = byte_range_to_link(db, config, request)
    yield dumps({"link": link}).encode("utf8")


if __name__ == "__main__":
    CGIHandler().run(alignment_to_text)
