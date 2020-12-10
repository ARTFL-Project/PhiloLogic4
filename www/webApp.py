#!/usr/bin/env python3
"""Bootstrap Web app"""


import imp
import os.path
import sys
import shutil

from philologic.runtime import WebConfig
from philologic.runtime import WSGIHandler
from philologic.runtime import access_control

PATH = os.path.abspath(os.path.dirname(__file__))

def start_web_app(environ, start_response):
    config = WebConfig(os.path.abspath(PATH))
    headers = [("Content-type", "text/html; charset=UTF-8"), ("Access-Control-Allow-Origin", "*")]
    if not config.valid_config:  # This means we have an error in the webconfig file
        html = build_misconfig_page(config.traceback, "webconfig.cfg")
    # TODO handle errors in db.locals.py
    else:
        request = WSGIHandler(environ, config)
        if config.access_control:
            if not request.authenticated:
                token = access_control.check_access(environ, config)
                if token:
                    h, ts = token
                    headers.append(("Set-Cookie", "hash=%s" % h))
                    headers.append(("Set-Cookie", "timestamp=%s" % ts))
        with open(f"{config.db_path}/app/dist/index.html") as index_page:
            html_page = index_page.read()
    start_response("200 OK", headers)
    return html_page


def build_misconfig_page(traceback, config_file):
    html_page = open("%s/app/misconfiguration.html" % PATH).read()
    html_page = html_page.replace("$TRACEBACK", traceback)
    html_page = html_page.replace("$config_FILE", config_file)
    return html_page
