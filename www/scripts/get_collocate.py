#!/usr/bin/env python

import os
import sys
sys.path.append('..')
from functions.wsgi_handler import parse_cgi
from wsgiref.handlers import CGIHandler
import reports as r
import json

def get_collocate(environ,start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    environ["SCRIPT_FILENAME"] = environ["SCRIPT_FILENAME"].replace('scripts/get_collocate.py', '')
    db, path_components, q = parse_cgi(environ)
    hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
    results = r.fetch_collocation(hits, environ["SCRIPT_FILENAME"], q, db, full_report=False)
    results_with_links = {}
    for word, num in results:
        url = r.link_to_concordance(q, word, 'all', num)
        results_with_links[word] = {'count': num, 'url': url}
    yield json.dumps(results_with_links,indent=2)
    
if __name__ == "__main__":
    CGIHandler().run(get_collocate)

