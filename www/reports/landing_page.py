#!/usr/bin/env python

import os
import sys
sys.path.append('..')
from functions.wsgi_handler import wsgi_response, parse_cgi
import functions as f


def landing_page(environ,start_response):
    wsgi_response(environ, start_response)
    db, path_components, q = parse_cgi(environ)
    dbname = os.path.basename(environ["SCRIPT_FILENAME"].replace("/dispatcher.py",""))
    config = f.WebConfig()
    path = os.getcwd()
    return f.render_template(db=db,dbname=dbname, q=q, template_name='landing_page.mako', config=config, report="landing_page")
