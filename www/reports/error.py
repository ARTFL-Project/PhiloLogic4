#!/usr/bin/env python

import os
import sys
sys.path.append('..')
import functions as f
import reports as r
import json
from philologic.HitList import NoHits
from functions.wsgi_handler import wsgi_response, parse_cgi


def error(environ,start_response):
    try:
        db, dbname, path_components, q = wsgi_response(environ,start_response)
    except AssertionError:
        myname = environ["SCRIPT_FILENAME"]
        dbname = os.path.basename(myname.replace("/dispatcher.py",""))
        db, path_components, q = parse_cgi(environ)
    return error_handling(db, dbname, q)
    
def error_handling(db, dbname, q):
    hits = NoHits()
    path = os.getcwd().replace('functions/', '')
    config = f.WebConfig()
    if q["error_report"]:
        report = q["error_report"]
    else:
        report = q['report']
    print >> sys.stderr, "ERRORRRRR", report
    hits = NoHits()
    if report == "concordance":
        return r.render_concordance(hits, db, dbname, q, path, config)
    elif report == "kwic":
        return r.render_kwic(hits, db, dbname, q, path, config)
    elif report == "collocation":
        return r.render_collocation(hits, db, dbname, q, path, config)
    elif report == "time_series":
        q = r.handle_dates(q, db)
        return r.render_time_series(hits, db, dbname, q, path, config)
    
#def error(environ,start_response):
#    config = f.WebConfig()
#    try:
#        db, dbname, path_components, q = wsgi_response(environ,start_response)
#    except AssertionError:
#        myname = environ["SCRIPT_FILENAME"]
#        dbname = os.path.basename(myname.replace("/dispatcher.py",""))
#        db, path_components, q = parse_cgi(environ)
#    return render_template(db=db,dbname=dbname,form=True, q=q, config=config,
#                           report="error", template_name='error.mako')

