#!/usr/bin/env python

import sys
sys.path.append('..')
import functions as f
import os
import re
from functions.wsgi_handler import wsgi_response
from bibliography import bibliography
from render_template import render_template
from functions.ObjectFormatter import format_concordance, format_strip, convert_entities, adjust_bytes
from functions.FragmentParser import parse

def frequencies(environ,start_response):
    db, dbname, path_components, q = wsgi_response(environ,start_response)
    path = os.getcwd().replace('functions/', '')
    results = prominent_features(q, db)
    #hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
    #return render_template(results=hits,db=db,dbname=dbname,q=q,fetch_concordance=fetch_concordance,
    #                       f=f, path=path, results_per_page=q['results_per_page'],
    #                       template_name="concordance.mako")
    
def prominent_features(q):
    conn = db.dbh
    c = conn.cursor()
    
