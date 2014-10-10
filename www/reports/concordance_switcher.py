#!/usr/bin/env python

import sys
sys.path.append('..')
import functions as f
import os
import cgi
from functions.wsgi_handler import parse_cgi
from bibliography import bibliography
from render_template import render_template
from concordance import fetch_concordance
from kwic import fetch_kwic
from mako.template import Template
    
if __name__ == "__main__":
    environ = os.environ
    environ["SCRIPT_FILENAME"] = environ["SCRIPT_FILENAME"].replace('reports/concordance_switcher.py', '')
    form = cgi.FieldStorage()
    dbname = os.path.basename(environ["SCRIPT_FILENAME"])
    path = os.getcwd().replace('reports', '')
    config = f.WebConfig()
    db, path_components, q = parse_cgi(environ)
    try:
        hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
    except:
        hits = noHits()
    print "Content-Type: text/html\n"
    if q['report'] == 'concordance':
        mytemplate = Template(filename=path + "templates/concordance_short.mako")
        print mytemplate.render(results=hits,db=db,dbname=dbname,q=q,fetch_concordance=fetch_concordance,f=f,
                                config=config, path=path, results_per_page=q['results_per_page']).encode('utf-8', 'ignore')
    else:
        mytemplate = Template(filename=path + "templates/kwic_short.mako")
        print >> sys.stderr, mytemplate.render(results=hits,db=db,dbname=dbname,q=q,fetch_kwic=fetch_kwic,f=f,
                                config=config, path=path, results_per_page=q['results_per_page']).encode('utf-8', 'ignore')
        print mytemplate.render(results=hits,db=db,dbname=dbname,q=q,fetch_kwic=fetch_kwic,f=f,
                                config=config, path=path, results_per_page=q['results_per_page']).encode('utf-8', 'ignore')
        