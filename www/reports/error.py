#!/usr/bin/env python

import os
import sys
sys.path.append('..')
import functions as f
from functions import log_config
import logging
from functions.wsgi_handler import wsgi_response, parse_cgi
from render_template import render_template


def error(environ,start_response):
    config = f.WebConfig()
    try:
        db, dbname, path_components, q = wsgi_response(environ,start_response)
    except AssertionError:
        myname = environ["SCRIPT_FILENAME"]
        dbname = os.path.basename(myname.replace("/dispatcher.py",""))
        db, path_components, q = parse_cgi(environ)
    logging.error("Query string: %s" % q['q_string'])
    return render_template(db=db,dbname=dbname,form=True, q=q, config=config,
                           report="error", template_name='error.mako')
