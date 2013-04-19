#!/usr/bin/env python

import os
import sys
sys.path.append('..')
from functions.wsgi_handler import parse_cgi
import reports as r
import cgi
from json import dumps

    
if __name__ == "__main__":
    environ = os.environ
    environ["SCRIPT_FILENAME"] = environ["SCRIPT_FILENAME"].replace('scripts/collocation_fetcher.py', '')
    form = cgi.FieldStorage()
    db, path_components, q = parse_cgi(environ)
    hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
    #print >> sys.stderr, q['colloc_start'], q['colloc_end']
    all_colloc, left_colloc, right_colloc = r.fetch_collocation(hits, environ["SCRIPT_FILENAME"], q)
    print "Content-Type: text/html\n"
    print dumps([all_colloc, left_colloc, right_colloc])