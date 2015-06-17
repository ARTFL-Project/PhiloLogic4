#!/usr/bin/env python

import sys
sys.path.append('..')
import functions as f
import reports as r
import os
import re
from philologic.DB import DB
from functions.wsgi_handler import WSGIHandler
from wsgiref.handlers import CGIHandler
from concordance import concordance_citation, citation_links
from functions.ObjectFormatter import format_strip, convert_entities, adjust_bytes
try:
    import simplejson as json
except ImportError:
    print >> sys.stderr, "Import Error, please install simplejson for better performance"
    import json


def kwic(environ,start_response):
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    kwic_object = generate_kwic_results(db, request, config)
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response('200 OK',headers)
    yield json.dumps(kwic_object)

def generate_kwic_results(db, q, config, link_to_hit="div1"):
    """ The link_to_hit keyword defines the text object to which the metadata link leads to"""
    hits = db.query(q["q"],q["method"],q["arg"],**q.metadata)
    start, end, n = f.link.page_interval(q.results_per_page, hits, q.start, q.end)
    kwic_object = {"description": {"start": start, "end": end, "results_per_page": q.results_per_page},
                    "query": dict([i for i in q])}
    kwic_results = []
    
    length = config.concordance_length
    
    for hit in hits[start - 1:end]:
        # Get all metadata
        metadata_fields = {}
        for metadata in db.locals['metadata_fields']:
            metadata_fields[metadata] = hit[metadata].strip()
        
        ## Get all links and citations
        citation_hrefs = citation_links(db, config, hit)
        citation = concordance_citation(hit, citation_hrefs)
            
        ## Determine length of text needed
        byte_distance = hit.bytes[-1] - hit.bytes[0]
        length = config.concordance_length + byte_distance + config.concordance_length
            
        ## Get concordance and align it
        bytes, byte_start = adjust_bytes(hit.bytes, config.concordance_length)
        conc_text = f.get_text(hit, byte_start, length, config.db_path)
        conc_text = format_strip(conc_text, bytes)
        conc_text = KWIC_formatter(conc_text, len(hit.bytes))

        kwic_result = {"philo_id": hit.philo_id, "context": conc_text, "metadata_fields": metadata_fields,
                       "citation_links": citation_hrefs, "citation": citation, "bytes": hit.bytes}
        kwic_results.append(kwic_result)
    kwic_object['results'] = kwic_results
    kwic_object['results_length'] = len(hits)
    kwic_object["query_done"] = hits.done
    
    return kwic_object

def KWIC_formatter(output, hit_num, chars=40):
    output = output.replace('\n', ' ')
    output = output.replace('\r', '')
    output = output.replace('\t', ' ')
    try:
        start_hit = output.index('<span class="highlight">')
    except ValueError:
        return output
    start_output = '<span class="kwic-before"><span class="inner-before">' + output[:start_hit] + '</span></span>'
    end_hit = output.rindex('</span>') + 7
    end_output = '<span class="kwic-after">' + output[end_hit:] + '</span>'
    return '<span class="kwic-text">' + start_output + '&nbsp;<span class="kwic-highlight">' + output[start_hit:end_hit] + "</span>&nbsp;" + end_output + '</span>'

if __name__ == "__main__":
    CGIHandler().run(kwic)