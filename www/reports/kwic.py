#!/usr/bin/env python

import sys
sys.path.append('..')
import functions as f
import os
import re
from functions.wsgi_handler import wsgi_response
from bibliography import bibliography
from render_template import render_template


def kwic(environ,start_response):
    db, dbname, path_components, q = wsgi_response(environ,start_response)
    path = os.getcwd().replace('functions/', '')
    if q['q'] == '':
        return bibliography(f,path, db, dbname,q,environ)
    else:
        hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
        return render_template(results=hits,db=db,dbname=dbname,q=q,fetch_kwic=fetch_kwic,f=f,
                                path=path, results_per_page=q['results_per_page'], template_name='kwic.mako')

def fetch_kwic(results, path, q, byte_query, start, end, length=400):
    kwic_results = []
    shortest_biblio = 0

    for hit in results[start:end]:
        biblio = hit.articleAuthor + ', ' +  hit.head
        
        ## additional clean-up for titles
        biblio = ' '.join(biblio.split()) ## maybe hackish, but it works
        
        get_query = byte_query(hit.bytes)
        href = "./" + '/'.join([str(i) for i in hit.philo_id[:4]]) + get_query
        
        ## Find shortest bibliography entry
        biblio = biblio
        if shortest_biblio == 0:
            shortest_biblio = len(biblio)
        if len(biblio) < shortest_biblio:
            shortest_biblio = len(biblio)
            
        ## Determine length of text needed
        byte_distance = hit.bytes[-1] - hit.bytes[0]
        length = 200 + byte_distance + 200
            
        ## Get concordance and align it
        bytes, byte_start = f.format.adjust_bytes(hit.bytes, length)
        conc_text = f.get_text(hit, byte_start, length, path)
        conc_start, conc_middle, conc_end = f.format.chunkifier(conc_text, bytes, highlight=True, kwic=True)
        conc_start = f.format.clean_text(conc_start, kwic=True)
        conc_end = f.format.clean_text(conc_end, kwic=True)
        conc_middle = f.format.clean_text(conc_middle, notag=False, kwic=True)
        conc_text = (conc_start + conc_middle + conc_end).decode('utf-8', 'ignore')
        conc_text = f.format.align_text(conc_text, len(hit.bytes))
        kwic_results.append((biblio, href, conc_text, hit))
        
    if shortest_biblio < 20:
        shortest_biblio = 20
    
    ## Populate Kwic_results with bibliography    
    for pos, result in enumerate(kwic_results):
        biblio, href, text, hit = result
        if len(biblio) < 20:
            diff = 20 - len(biblio)
            biblio += ' ' * diff
        short_biblio = '<span id="short_biblio" style="white-space:pre-wrap;">%s</span>' % biblio[:shortest_biblio]
        full_biblio = '<span id="full_biblio" style="display:none;">%s</span>' % biblio
        kwic_biblio = full_biblio + short_biblio
        kwic_biblio_link = '<a href="%s" class="kwic_biblio" style="white-space:pre-wrap;">' % href + kwic_biblio + '</a>: '
        kwic_results[pos] = kwic_biblio_link + '<span id="kwic_text">%s</span>' % text
    return kwic_results
