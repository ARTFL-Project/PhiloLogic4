#!/usr/bin/env python

import os
import sys
sys.path.append('..')
from functions.wsgi_handler import wsgi_response
from render_template import render_template
import functions as f
from functions import concatenate_files


def landing_page(environ,start_response):
    db, dbname, path_components, q = wsgi_response(environ,start_response)
    config = f.WebConfig()
    path = os.getcwd()
    concatenate_files(path, "landing_page", debug=db.locals["debug"])
    return render_template(db=db,dbname=dbname,form=True, q=q, template_name='landing_page.mako',
                           config=config, report="landing_page")
