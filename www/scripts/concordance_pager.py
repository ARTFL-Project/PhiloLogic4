#!/usr/bin/env python

import sys
sys.path.append('..')
import functions as f
import reports as r
from philologic.DB import DB
from wsgiref.handlers import CGIHandler
from functions.wsgi_handler import WSGIHandler
from mako.template import Template
    

def concordance_pager(environ,start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    if request['report'] == 'concordance':
        concordance_object, hits = r.concordance_results(db, request, config)
        mytemplate = Template(filename=config.db_path + "templates/concordance_short.mako")
        yield mytemplate.render(concordance=concordance_object,query_string=request.query_string, config=config).encode('utf-8', 'ignore')
    else:
        kwic_object, hits = r.generate_kwic_results(db, request, config)
        mytemplate = Template(filename=config.db_path + "templates/kwic_short.mako")
        yield mytemplate.render(kwic=kwic_object,query_string=request.query_string,config=config).encode('utf-8', 'ignore')
        
if __name__ == "__main__":
    CGIHandler().run(concordance_kwic_switcher)