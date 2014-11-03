#!/usr/bin/env python

import sys
sys.path.append('..')
import functions as f
import reports as r
import os
import cgi
from wsgiref.handlers import CGIHandler
from functions.wsgi_handler import parse_cgi
from mako.template import Template
    

def concordance_kwic_switcher(environ,start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    environ = os.environ
    environ["SCRIPT_FILENAME"] = environ["SCRIPT_FILENAME"].replace('scripts/concordance_kwic_switcher.py', '')
    form = cgi.FieldStorage()
    path = os.getcwd().replace('scripts', '')
    config = f.WebConfig()
    db, path_components, q = parse_cgi(environ)
    if q['report'] == 'concordance':
        concordance_object, hits = r.concordance_results(db, q, config, path)
        mytemplate = Template(filename=path + "templates/concordance_short.mako")
        yield mytemplate.render(concordance=concordance_object,q=q, config=config).encode('utf-8', 'ignore')
    else:
        kwic_object, hits = r.generate_kwic_results(db, q, config, path)
        mytemplate = Template(filename=path + "templates/kwic_short.mako")
        yield mytemplate.render(kwic=kwic_object,q=q,config=config).encode('utf-8', 'ignore')
        
if __name__ == "__main__":
    CGIHandler().run(concordance_kwic_switcher)