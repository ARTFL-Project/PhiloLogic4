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
    environ["SCRIPT_FILENAME"] = environ["SCRIPT_FILENAME"].replace('scripts/report_switcher.py', '')
    form = cgi.FieldStorage()
    db, path_components, q = parse_cgi(environ)
    if q['report'] == "concordance" or q['report'] == "kwic":
        hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
    elif q['report'] == "frequency":
        hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
        hits = r.frequency.generate_frequency(hits, q, db)
    elif q['report'] == 'relevance':
        hits = r.relevance.retrieve_hits(q, db)
    elif q['report'] == 'time_series':
        frequencies, relative_frequencies = r.time_series.generate_frequency(q, db)
    elif q['report'] == 'collocation':
        hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
        results = fetch_collocation(hits, path, q)
    print "Content-Type: text/html\n"
    print json.dumps(results)    