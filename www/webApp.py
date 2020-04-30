#!/usr/bin/env python3
"""Bootstrap Web app"""


import imp
import os.path
import sys
import shutil

from philologic5.runtime import WebConfig
from philologic5.runtime import WSGIHandler
from philologic5.runtime import access_control

config = WebConfig(os.path.abspath(os.path.dirname(__file__)))
global_config = imp.load_source("philologic4", config.global_config_location)
path = os.path.abspath(os.path.dirname(__file__))
dbname = path.strip().split("/")[-1]

config = WebConfig(os.path.abspath(os.path.dirname(__file__)))
config_location = os.path.join("app/assets/css/split/", os.path.basename(config.theme))
if os.path.realpath(os.path.abspath(config.theme)) == os.path.realpath(os.path.abspath(config_location)):
    theme = config_location
elif os.path.exists(config_location) and config.production:
    theme = config_location
else:
    os.system("cp %s %s" % (config.theme, config_location))
    theme = config_location


def start_web_app(environ, start_response):
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
    html_page = open("%s/app/misconfiguration.html" % path).read()
    html_page = html_page.replace("$TRACEBACK", traceback)
    html_page = html_page.replace("$CONFIG_FILE", config_file)
    return html_page
