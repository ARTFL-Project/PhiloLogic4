#!/usr/bin/env python

import sys
sys.path.append('..')
from functions.wsgi_handler import wsgi_response
from render_template import render_template
import functions as f


def landing_page(environ,start_response):
    db, dbname, path_components, q = wsgi_response(environ,start_response)
    config = f.WebConfig()
    print >> sys.stderr, "CONCORDANCE", config.search_examples
    #search_examples = f.search_examples(db, config)
    return render_template(db=db,dbname=dbname,form=True, q=q, template_name='landing_page.mako',
                           config=config, report="landing_page")
