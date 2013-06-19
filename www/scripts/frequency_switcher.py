#!/usr/bin/env python

import os
import sys
sys.path.append('..')
from functions.wsgi_handler import parse_cgi
from mako.template import Template
import reports as r
import cgi

    
if __name__ == "__main__":
    environ = os.environ
    environ["SCRIPT_FILENAME"] = environ["SCRIPT_FILENAME"].replace('scripts/frequency_switcher.py', '')
    path = environ["SCRIPT_FILENAME"]
    form = cgi.FieldStorage()
    frequency_field = form.getvalue('frequency_field')
    db, path_components, q = parse_cgi(environ)
    hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
    field, results = r.generate_frequency(hits, q, db)
    mytemplate = Template(filename=path + "templates/frequency_short.mako")
    print "Content-Type: text/html\n"
    print mytemplate.render(frequency_field=field,counts=results).encode('utf-8', 'ignore')