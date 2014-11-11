#!/usr/bin/env python

import os
import sys
sys.path.append('..')
from functions.wsgi_handler import wsgi_response, parse_cgi
from render_template import render_template
import functions as f


def landing_page(environ,start_response):
    wsgi_response(environ, start_response)
    db, path_components, q = parse_cgi(environ)
    dbname = os.path.basename(environ["SCRIPT_FILENAME"].replace("/dispatcher.py",""))
    config = f.WebConfig()
    path = os.getcwd()
    resource = f.webResources("landing_page", debug=db.locals["debug"])
    return render_template(db=db,dbname=dbname,form=True, q=q, template_name='landing_page.mako',
                           config=config, report="landing_page", css=resource.css, js=resource.js)
