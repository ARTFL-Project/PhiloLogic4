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
    environ["SCRIPT_FILENAME"] = environ["SCRIPT_FILENAME"].replace('scripts/get_collocate.py', '')
    db, path_components, q = parse_cgi(environ)
    hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
    results = r.fetch_collocation(hits, environ["SCRIPT_FILENAME"], q, db, full_report=False)
    results_with_links = []
    for word, num in results:
        url = r.link_to_concordance(q, word, 'all', num)
        results_with_links.append((word, num, url))
    print "Content-Type: text/html\n"
    print json.dumps(results_with_links,indent=2)
