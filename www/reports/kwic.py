#!/usr/bin/env python

import sys
sys.path.append('..')
import functions as f
import os
import re
from functions.wsgi_handler import wsgi_response
from bibliography import fetch_bibliography as bibliography
from render_template import render_template
from functions.ObjectFormatter import format_strip, convert_entities, adjust_bytes


def kwic(environ,start_response):
    db, dbname, path_components, q = wsgi_response(environ,start_response)
    path = os.getcwd().replace('functions/', '')
    if q['q'] == '':
        return bibliography(f,path, db, dbname,q,environ)
    else:
        hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
        return render_template(results=hits,db=db,dbname=dbname,q=q,fetch_kwic=fetch_kwic,f=f,
                                path=path, results_per_page=q['results_per_page'],
                                template_name='kwic.mako', report="kwic")

def fetch_kwic(results, path, q, byte_query, db, start, end, length=500):
    kwic_results = []
    shortest_biblio = 0

    for hit in results[start:end]:
        biblio = hit.author + ', ' +  hit.title
        
        ## additional clean-up for titles
        biblio = ' '.join(biblio.split()) ## maybe hackish, but it works
        
        get_query = byte_query(hit.bytes)
        href = "./" + '/'.join([str(i) for i in hit.philo_id[:2]]) + get_query
        
        ## Find shortest bibliography entry
        biblio = biblio
        if shortest_biblio == 0:
            shortest_biblio = len(biblio)
        if len(biblio) < shortest_biblio:
            shortest_biblio = len(biblio)
            
        ## Determine length of text needed
        byte_distance = hit.bytes[-1] - hit.bytes[0]
        length = length/2 + byte_distance + length/2
            
        ## Get concordance and align it
        bytes, byte_start = adjust_bytes(hit.bytes, length)
        conc_text = f.get_text(hit, byte_start, length, path)
        conc_text = format_strip(conc_text, bytes)
        conc_text = KWIC_formatter(conc_text, len(hit.bytes))
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


def KWIC_formatter(output, hit_num, chars=40):
    output = output.replace('\n', ' ')
    output = output.replace('\r', '')
    output = output.replace('\t', ' ')
    output = re.sub(' {2,}', ' ', output)
    output = convert_entities(output)
    start_hit = output.index('<span class="highlight">')
    end_hit = output.rindex('</span>') + 7
    tag_length = 7 * hit_num
    start_output = output[start_hit - chars:start_hit]
    start_output = re.sub('^[^ ]+? ', ' ', start_output, 1) # Do we want to keep this?
    if len(start_output) < chars:
        white_space = ' ' * (chars - len(start_output))
        start_output = white_space + start_output
    start_output = '<span style="white-space:pre-wrap;">' + start_output + '</span>'
    end_output = re.sub('[^ ]+\Z', ' ', output[end_hit:], 1)
    match = output[start_hit:end_hit]
    return start_output + match + end_output[:chars+tag_length]
