#!/usr/bin/env python

import sys
sys.path.append('..')
from functions.wsgi_handler import WSGIHandler
from wsgiref.handlers import CGIHandler
import reports as r
import json

def get_start_end_date(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    config = f.WebConfig()
    yield config.toJSON()
    
if __name__ == "__main__":
    CGIHandler().run(get_web_config)