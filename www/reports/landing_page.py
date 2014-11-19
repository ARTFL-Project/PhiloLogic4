#!/usr/bin/env python

import os
import sys
sys.path.append('..')
from functions.wsgi_handler import WSGIHandler
from philologic.DB import DB
import functions as f


def landing_page(environ,start_response):
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    headers = [('Content-type', 'text/html; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response('200 OK',headers)
    return f.render_template(query_string=request.query_string, template_name='landing_page.mako', config=config, report="landing_page")