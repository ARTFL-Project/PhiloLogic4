#!/usr/bin/env python

import sys
sys.path.append('..')
import functions as f
import os
from functions.wsgi_handler import wsgi_response
from bibliography import bibliography
from render_template import render_template

def concordance(environ,start_response):
    db, dbname, path_components, q = wsgi_response(environ,start_response)
    path = os.getcwd().replace('functions/', '')
    if q['q'] == '':
        return bibliography(f,path, db, dbname,q,environ)
    else:
        hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
        return render_template(results=hits,db=db,dbname=dbname,q=q,fetch_concordance=fetch_concordance,f=f,
                                path=path, results_per_page=q['results_per_page'], template_name="concordance.mako")

def fetch_concordance(hit, path, q):
    ## Determine length of text needed
    byte_distance = hit.bytes[-1] - hit.bytes[0]
    length = 1000 + byte_distance + 1000
    
    bytes, byte_start = f.format.adjust_bytes(hit.bytes, length)
    conc_text = f.get_text(hit, byte_start, length, path)
    conc_start, conc_middle, conc_end = f.format.chunkifier(conc_text, bytes, highlight=True)
    conc_start = f.format.clean_text(conc_start)
    conc_end = f.format.clean_text(conc_end)
    conc_text = conc_start + conc_middle + conc_end
    conc_text = conc_text.decode('utf-8', 'ignore')
    start_highlight = conc_text.find('<span class="highlight"')
    end_highlight = conc_text.rfind('</span>')
    begin = start_highlight - 200
    end = end_highlight + 200
    min = bytes[-1] + len("<span class='highlight'></span>") * len(bytes)
    if end < min:
        end = min
    first_span = '<span class="begin_concordance" style="display:none;">'
    second_span = '<span class="end_concordance" style="display:none;">'
    conc_text =  first_span + conc_text[:begin] + '</span>' + conc_text[begin:end] + second_span + conc_text[end:] + '</span>'
    return conc_text
    
