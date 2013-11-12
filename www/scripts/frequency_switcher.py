#!/usr/bin/env python

import os
import sys
sys.path.append('..')
from functions.wsgi_handler import parse_cgi
from wsgiref.handlers import CGIHandler
from mako.template import Template
import reports as r
import cgi

def frequency_switcher(environ,start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    environ["SCRIPT_FILENAME"] = environ["SCRIPT_FILENAME"].replace('scripts/frequency_switcher.py', '')
    cgi = urlparse.parse_qs(environ["QUERY_STRING"],keep_blank_values=True)
    frequency_field = cgi.get('frequency_field',[''])[0]
    db, path_components, q = parse_cgi(environ)
    hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
    field, results = r.generate_frequency(hits, q, db)
    mytemplate = Template(filename=path + "templates/frequency_short.mako")
    yield mytemplate.render(frequency_field=field,counts=results).encode('utf-8', 'ignore')

if __name__ == "__main__":
    CGIHandler().run(frequency_switcher)
