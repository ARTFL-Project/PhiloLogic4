#!/usr/bin/env python

import os
import re
import sys
sys.path.append('..')
from functions.wsgi_handler import parse_cgi
from reports.concordance import fetch_concordance
from reports.theme_rheme import adjust_results
import cgi
import json
from philologic.DB import DB


    
if __name__ == "__main__":
    environ = os.environ
    path = environ['SCRIPT_FILENAME']
    path = re.sub('(philo4/[^/]+/).*', '\\1', path)
    form = cgi.FieldStorage()
    num = int(form.getvalue('hit_num'))
    length = int(form.getvalue('length'))
    db, path_components, q = parse_cgi(environ)
    hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
    if q['report'] != 'theme_rheme':
        conc_text = fetch_concordance(hits[num], path, q, length=length)
    else:
        new_hits, full_report = adjust_results(hits, path, q, length=length)
        conc_text = new_hits[num].concordance
    print "Content-Type: text/html\n"
    print conc_text.encode('utf-8', 'ignore')
    