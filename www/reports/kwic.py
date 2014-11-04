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
    if q['q'] == '':
        return bibliography(f,path, db, dbname,q,environ)
    else:
        kwic_object, hits = generate_kwic_results(db, q, config, path)
        if q['format'] == "json":
            # Remove db_path from query object since we don't want to expose that info to the client
            del concordance_object['query']['dbpath']
            return json.dumps(kwic_object)
        return render_kwic(kwic_object, hits, db, dbname, q, path, config)
        
def render_kwic(kwic_object, hits, db, dbname, q, path, config):
    biblio_criteria = f.biblio_criteria(q, config)
    resource = f.webResources("kwic", debug=db.locals["debug"])
    pages = f.link.generate_page_links(kwic_object['description']['start'], q['results_per_page'], q, hits)
    return render_template(kwic=kwic_object,db=db,dbname=dbname,q=q, path=path, biblio_criteria=biblio_criteria,
                           pages=pages, config=config, template_name='kwic.mako', report="kwic", css=resource.css, js=resource.js)

def generate_kwic_results(db, q, config, path, length=5000):
    hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
    start, end, n = f.link.page_interval(q['results_per_page'], hits, q["start"], q["end"])
    kwic_object = {"description": {"start": start, "end": end, "n": n, "results_per_page": q['results_per_page']},
                    "query": q}
    kwic_results = []
    default_short_citation_len = 30
    short_citation_len = 0
  
    for hit in hits[start:end]:
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
        
        # Get all metadata
        metadata_fields = {}
        for metadata in q['metadata']:
            metadata_fields[metadata] = hit[metadata]
            
        kwic_results.append((full_citation, short_citation, href, conc_text, hit, metadata_fields))
    
    if short_citation_len < default_short_citation_len:
        default_short_citation_len = short_citation_len
    
    ## Populate Kwic_results with bibliography    
    for pos, result in enumerate(kwic_results):
        biblio, short_biblio, href, text, hit, metadata_fields = result
        if len(short_biblio) < default_short_citation_len:
            diff = default_short_citation_len - len(short_biblio)
            short_biblio += '&nbsp;' * diff
        short_biblio = '<span class="short_biblio">%s</span>' % short_biblio
        full_biblio = '<span class="full_biblio" style="display:none;">%s</span>' % biblio
        kwic_biblio = full_biblio + short_biblio
        kwic_biblio_link = '<a href="%s" class="kwic_biblio">' % href + kwic_biblio + '</a>: '
        kwic_results[pos] = {"philo_id": hit.philo_id, "context": kwic_biblio_link + '%s' % text, "metadata_fields": metadata_fields, "bytes": hit.bytes}

    kwic_object['results'] = kwic_results
    kwic_object['results_len'] = len(hits)
    kwic_object["query_done"] = hits.done
    
    return kwic_object, hits


def KWIC_formatter(output, hit_num, chars=40):
    output = output.replace('\n', ' ')
    output = output.replace('\r', '')
    output = output.replace('\t', ' ')
    start_hit = output.index('<span class="highlight">')
    start_output = '<span class="kwic-before"><span class="inner-before">' + output[:start_hit] + '</span></span>'
    end_hit = output.rindex('</span>') + 7
    end_output = '<span class="kwic-after">' + output[end_hit:] + '</span>'
    return '<span class="kwic-text">' + start_output + '&nbsp;<span class="kwic-highlight">' + output[start_hit:end_hit] + "</span>&nbsp;" + end_output + '</span>'
