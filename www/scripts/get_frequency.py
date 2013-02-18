#!/usr/bin/env python

import os
import sys
sys.path.append('..')
from functions.wsgi_handler import parse_cgi
import reports as r
import cgi
import json

    
if __name__ == "__main__":
    environ = os.environ
    environ["SCRIPT_FILENAME"] = environ["SCRIPT_FILENAME"].replace('scripts/get_frequency.py', '')
    form = cgi.FieldStorage()
    frequency_field = form.getvalue('frequency_field')
    db, path_components, q = parse_cgi(environ)
    q['field'] = frequency_field
    hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
    field, results = r.generate_frequency(hits, q, db)
    print "Content-Type: text/html\n"
    print json.dumps(results)
    print >> sys.stderr, environ["QUERY_STRING"]
    