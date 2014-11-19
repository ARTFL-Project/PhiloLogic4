#!/usr/bin/env python

import sys
sys.path.append('..')
import functions as f
import reports as r
import os
import re
from philologic.DB import DB
from functions.wsgi_handler import wsgi_response, WSGIHandler
from concordance import concordance_citation, citation_links
from functions.ObjectFormatter import format_strip, convert_entities, adjust_bytes
import json


def kwic(environ,start_response):
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    if request.no_q:
        return r.fetch_bibliography(db, request, config, start_response)
    else:
        kwic_object, hits = generate_kwic_results(db, request, config)
        if request['format'] == "json":
            headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
            start_response('200 OK',headers)
            return json.dumps(kwic_object)
        headers = [('Content-type', 'text/html; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
        start_response('200 OK',headers)
        return render_kwic(kwic_object, hits, config, request)
        
def render_kwic(k, hits, config, q):
    biblio_criteria = f.biblio_criteria(q, config)
    pages = f.link.generate_page_links(k['description']['start'], q.results_per_page, q, hits)
    return f.render_template(kwic=k, query_string=q.query_string, biblio_criteria=biblio_criteria,
                             pages=pages, config=config, template_name='kwic.mako', report="kwic")

def generate_kwic_results(db, q, config, length=5000, link_to_hit="div1"):
    """ The link_to_hit keyword defines the text object to which the metadata link leads to"""
    hits = db.query(q["q"],q["method"],q["arg"],**q.metadata)
    start, end, n = f.link.page_interval(q.results_per_page, hits, q.start, q.end)
    kwic_object = {"description": {"start": start, "end": end, "n": n, "results_per_page": q.results_per_page},
                    "query": dict([i for i in q])}
    kwic_results = []
    default_short_citation_len = 30
    short_citation_len = 0
    
    for hit in hits[start - 1:end]:
        # Get all metadata
        metadata_fields = {}
        for metadata in db.locals['metadata_fields']:
            metadata_fields[metadata] = hit[metadata]
        
        ## Get all links and citations
        citation_hrefs = citation_links(db, config, hit)
        full_citation, short_citation = kwic_citation(short_citation_len, metadata_fields, hit[link_to_hit])
        
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
        conc_text = f.get_text(hit, byte_start, length, config.db_path)
        conc_text = format_strip(conc_text, bytes)
        conc_text = KWIC_formatter(conc_text, len(hit.bytes))
            
        kwic_results.append((full_citation, short_citation, citation_hrefs, conc_text, hit, metadata_fields))
    
    if short_citation_len < default_short_citation_len:
        default_short_citation_len = short_citation_len
    
    ## Populate Kwic_results with bibliography    
    for pos, result in enumerate(kwic_results):
        biblio, short_biblio, hrefs, text, hit, metadata_fields = result
        href = hrefs[link_to_hit]
        if len(short_biblio) < default_short_citation_len:
            diff = default_short_citation_len - len(short_biblio)
            short_biblio += '&nbsp;' * diff
        short_biblio = '<span class="short_biblio">%s</span>' % short_biblio
        full_biblio = '<span class="full_biblio" style="display:none;">%s</span>' % biblio
        kwic_biblio = full_biblio + short_biblio
        kwic_biblio_link = '<a href="%s" class="kwic_biblio">' % href + kwic_biblio + '</a>: '
        kwic_results[pos] = {"philo_id": hit.philo_id, "context": kwic_biblio_link + '%s' % text, "metadata_fields": metadata_fields,
                             "citation_links": hrefs, "citation": kwic_biblio_link, "bytes": hit.bytes}

    kwic_object['results'] = kwic_results
    kwic_object['results_length'] = len(hits)
    kwic_object["query_done"] = hits.done
    
    return kwic_object, hits

def kwic_citation(short_citation_length, metadata_fields, hit):
    full_citation = ""
    short_citation = []
    author = metadata_fields['author']
    if author:
        full_citation += author + ", "
    short_citation.append(author)
    title = metadata_fields['title']
    full_citation += title
    short_citation.append(title)
        
    if len(', '.join([s for s in short_citation if s])) > short_citation_length:
        short_author, short_title = tuple(short_citation)
        if len(short_author) > 10:
            short_author = short_author[:10] + "&#8230;"
            short_citation[0] = short_author
        title_len = short_citation_length - len(short_author)
        if len(short_title) > title_len:
            short_citation[1] = short_title[:title_len]
    short_citation = ', '.join([s for s in short_citation if s])
    
    full_citation += ', %s' % hit.head
    
    return full_citation, short_citation

def KWIC_formatter(output, hit_num, chars=40):
    output = output.replace('\n', ' ')
    output = output.replace('\r', '')
    output = output.replace('\t', ' ')
    start_hit = output.index('<span class="highlight">')
    start_output = '<span class="kwic-before"><span class="inner-before">' + output[:start_hit] + '</span></span>'
    end_hit = output.rindex('</span>') + 7
    end_output = '<span class="kwic-after">' + output[end_hit:] + '</span>'
    return '<span class="kwic-text">' + start_output + '&nbsp;<span class="kwic-highlight">' + output[start_hit:end_hit] + "</span>&nbsp;" + end_output + '</span>'
