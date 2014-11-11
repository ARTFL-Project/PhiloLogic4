#!/usr/bin/env python

import sys
sys.path.append('..')
import functions as f
import socket
from functions.wsgi_handler import wsgi_response
from render_template import render_template


def access(environ, start_response):
    db, dbname, path_components, q = wsgi_response(environ,start_response)
    config = f.WebConfig()
    incoming_address = environ['REMOTE_ADDR']
    hostname = socket.gethostname()
    resource = f.webResources("access", debug=db.locals["debug"])
    return render_template(db=db,dbname=dbname, config=config,form=True, client_address=incoming_address, q=q,
                           hostname=environ['HTTP_HOST'], report='access', template_name='access_denied.mako',
                           css=resource.css, js=resource.js)