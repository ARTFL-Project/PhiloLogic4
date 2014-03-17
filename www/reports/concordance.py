#!/usr/bin/env python

import sys
sys.path.append('..')
import functions as f
import os
import re
from functions.wsgi_handler import wsgi_response
from bibliography import fetch_bibliography as bibliography
from render_template import render_template
from functions.ObjectFormatter import format_concordance, convert_entities, adjust_bytes
from functions.FragmentParser import parse
import json

def concordance(environ,start_response):
    db, dbname, path_components, q = wsgi_response(environ,start_response)
    path = os.getcwd().replace('functions/', '')
    if q['format'] == "json":
        hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
        start, end, n = f.link.page_interval(q['results_per_page'], hits, q["start"], q["end"])
        formatted_results = [{"citation": f.cite.make_abs_div_cite(db,i),
                              "text": fetch_concordance(i, path, db)} for i in hits[start - 1:end]]
        return json.dumps(formatted_results)
    if q['q'] == '':
        return bibliography(f,path, db, dbname,q,environ)
    else:
        hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
        return render_template(results=hits,db=db,dbname=dbname,q=q,fetch_concordance=fetch_concordance,
                               f=f, path=path, results_per_page=q['results_per_page'],javascript="concordance.js",
                               template_name="concordance.mako", report="concordance")

def fetch_concordance(hit, path, q, context_size=1500):
    ## Determine length of text needed
    byte_distance = hit.bytes[-1] - hit.bytes[0]
    length = context_size + byte_distance + context_size
    bytes, byte_start = adjust_bytes(hit.bytes, length)
    conc_text = f.get_text(hit, byte_start, length, path)
    conc_text = format_concordance(conc_text, bytes)
    conc_text = convert_entities(conc_text)
        
    return conc_text
