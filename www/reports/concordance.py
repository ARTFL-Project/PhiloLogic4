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

def concordance(environ,start_response):
    db, dbname, path_components, q = wsgi_response(environ,start_response)
    path = os.getcwd().replace('functions/', '')
    if q['q'] == '':
        return bibliography(f,path, db, dbname,q,environ)
    else:
        hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
        return render_template(results=hits,db=db,dbname=dbname,q=q,fetch_concordance=fetch_concordance,
                               f=f, path=path, results_per_page=q['results_per_page'],
                               template_name="concordance.mako")

def fetch_concordance(hit, path, q):
    ## Determine length of text needed
    byte_distance = hit.bytes[-1] - hit.bytes[0]
    length = 750 + byte_distance + 750
    
    bytes, byte_start = adjust_bytes(hit.bytes, length)
    conc_text = f.get_text(hit, byte_start, length, path)
    conc_text = format_strip(conc_text, bytes)
    conc_text = convert_entities(conc_text)
    start_highlight = conc_text.find('<span class="highlight"')
    m = re.search(r'<span class="highlight">[^<]*?(</span>)',conc_text)
    if m:
        end_highlight = m.end(len(m.groups()) - 1)
        count = 0
        for char in reversed(conc_text[:start_highlight]):
            count += 1
            if count > 100 and char == ' ':
                break
        begin = start_highlight - count
        end = 0
        for char in conc_text[end_highlight:]:
            end += 1
            if end > 200 and char == ' ':
                break
        end += end_highlight
        first_span = '<span class="begin_concordance" style="display:none;">'
        second_span = '<span class="end_concordance" style="display:none;">'
        conc_text =  first_span + conc_text[:begin] + '</span>' + conc_text[begin:end] + second_span + conc_text[end:] + '</span>'
    return conc_text
