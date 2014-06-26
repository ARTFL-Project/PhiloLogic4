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
import json


def kwic(environ,start_response):
    db, dbname, path_components, q = wsgi_response(environ,start_response)
    path = os.getcwd().replace('functions/', '')
    config = f.WebConfig()
    if q['format'] == "json":
        hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
        start, end, n = f.link.page_interval(q['results_per_page'], hits, q["start"], q["end"])
        kwic_results = fetch_kwic(hits, path, q, f.link.byte_query, db, start-1, end, length=250)
        formatted_results = [{"citation": i[0],
                              "text": i[1]} for i in kwic_results]
        return json.dumps(formatted_results)
    if q['q'] == '':
        return bibliography(f,path, db, dbname,q,environ)
    else:
        hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
        return render_kwic(hits, db, dbname, q, path, config)
        
def render_kwic(hits, db, dbname, q, path, config):
    biblio_criteria = f.biblio_criteria(q, config)
    return render_template(results=hits,db=db,dbname=dbname,q=q,fetch_kwic=fetch_kwic,f=f,
                                path=path, results_per_page=q['results_per_page'], biblio_criteria=biblio_criteria,
                                config=config, template_name='kwic.mako', report="kwic")

def fetch_kwic(results, path, q, byte_query, db, start, end, length=5000):
    kwic_results = []
    
    default_short_citation_len = 30
    short_citation_len = 0
    for hit in results[start:end]:
        full_citation, short_citation, href = f.kwic_citation(db, hit, default_short_citation_len)
        
        ## Find longest short_citation
        if short_citation_len == 0:
            short_citation_len = len(short_citation)
        elif len(short_citation) > short_citation_len:
            short_citation_len = len(short_citation)
            
        ## Determine length of text needed
        byte_distance = hit.bytes[-1] - hit.bytes[0]
        length = length/2 + byte_distance + length/2
            
        ## Get concordance and align it
        bytes, byte_start = adjust_bytes(hit.bytes, length)
        conc_text = f.get_text(hit, byte_start, length, path)
        conc_text = format_strip(conc_text, bytes)
        conc_text = KWIC_formatter(conc_text, len(hit.bytes))
        kwic_results.append((full_citation, short_citation, href, conc_text, hit))
    
    #default_short_citation_len += 2 ## We add 2 to account for the comma and space separating both fields
    if short_citation_len < default_short_citation_len:
        default_short_citation_len = short_citation_len
    
    ## Populate Kwic_results with bibliography    
    for pos, result in enumerate(kwic_results):
        biblio, short_biblio, href, text, hit = result
        #print >> sys.stderr, "LEN", len(short_biblio),
        if len(short_biblio) < default_short_citation_len:
            #print >> sys.stderr, "DEFAULT", default_short_citation_len,
            diff = default_short_citation_len - len(short_biblio)
            short_biblio += '&nbsp;' * diff
        #print >> sys.stderr
        short_biblio = '<span class="short_biblio">%s</span>' % short_biblio
        full_biblio = '<span class="full_biblio" style="display:none;">%s</span>' % biblio
        kwic_biblio = full_biblio + short_biblio
        if q['format'] == "json":
            kwic_results[pos] = (kwic_biblio, text)
        else:
            kwic_biblio_link = '<a href="%s" class="kwic_biblio" style="white-space:pre-wrap;">' % href + kwic_biblio + '</a>: '
            kwic_results[pos] = kwic_biblio_link + '<span>%s</span>' % text
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
    #start_output = re.sub('^[^ ]+? ', ' ', start_output, 1) # Do we want to keep this?
    if len(start_output) < chars:
        white_space = ' ' * (chars - len(start_output))
        start_output = white_space + start_output
    start_output = '<span style="white-space:pre-wrap;">' + start_output + '</span>'
    end_output = re.sub('[^ ]+\Z', ' ', output[end_hit:], 1)
    match = output[start_hit:end_hit]
    return start_output + match + end_output[:chars+tag_length]
