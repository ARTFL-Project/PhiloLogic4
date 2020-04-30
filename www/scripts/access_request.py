#! /usr/bin/env python3

import os
from wsgiref.handlers import CGIHandler

import rapidjson
from philologic5.runtime import access_control, login_access

import sys

sys.path.append("..")
import custom_functions

try:
    from custom_functions import WebConfig
except ImportError:
    from philologic5.runtime import WebConfig
try:
    from custom_functions import WSGIHandler
except ImportError:
    from philologic5.runtime import WSGIHandler


default_reports = ["concordance", "kwic", "collocation", "time_series", "navigation"]


def access_request(environ, start_response):
    status = "200 OK"
    headers = [("Content-type", "application/json; charset=UTF-8"), ("Access-Control-Allow-Origin", "*")]
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace("scripts", ""))
    request = WSGIHandler(environ, config)
    access, headers = login_access(environ, request, config, headers)
    start_response(status, headers)
    if access:
        yield rapidjson.dumps({"access": True}).encode("utf8")
    else:
        incoming_address, domain_name = access_control.get_client_info(environ)
        yield rapidjson.dumps(
            {"access": False, "incoming_address": incoming_address, "domain_name": domain_name}
        ).encode("utf8")


if __name__ == "__main__":
    CGIHandler().run(access_request)
