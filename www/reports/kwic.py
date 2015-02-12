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
    if request.no_q:
        setattr(request, "report", "bibliography")
        return r.fetch_bibliography(db, request, config, start_response)
    else:
        kwic_object, hits = generate_kwic_results(db, request, config)
        headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
        start_response('200 OK',headers)
        return json.dumps(kwic_object)
        
def render_kwic(k, hits, config, q):
    biblio_criteria = f.biblio_criteria(q, config)
    pages = f.link.page_links(config,q,len(hits))
    collocation_script = f.link.make_absolute_query_link(config, q, report="collocation", format="json")
    frequency_script = f.link.make_absolute_query_link(config, q, script_name="/scripts/get_frequency.py", format="json")
    kwic_script = f.link.make_absolute_query_link(config, q, script_name="/scripts/concordance_kwic_switcher.py")
    concordance_script = f.link.make_absolute_query_link(config, q, script_name="/scripts/concordance_kwic_switcher.py", report="concordance")
    ajax_scripts = {"concordance": concordance_script, 'kwic': kwic_script, 'frequency': frequency_script, 'collocation': collocation_script}
    return f.render_template(kwic=k, query_string=q.query_string, biblio_criteria=biblio_criteria,
                             ajax=ajax_scripts, pages=pages, config=config, template_name='kwic.mako', report="kwic")

def generate_kwic_results(db, q, config, link_to_hit="div1"):
    """ The link_to_hit keyword defines the text object to which the metadata link leads to"""
    hits = db.query(q["q"],q["method"],q["arg"],**q.metadata)
    start, end, n = f.link.page_interval(q.results_per_page, hits, q.start, q.end)
    kwic_object = {"description": {"start": start, "end": end, "n": n, "results_per_page": q.results_per_page},
                    "query": dict([i for i in q])}
    kwic_results = []
    default_short_citation_len = 30
    shortest_citation_len = 0
    
    length = config.concordance_length
    
    for hit in hits[start - 1:end]:
        # Get all metadata
        metadata_fields = {}
        for metadata in db.locals['metadata_fields']:
            metadata_fields[metadata] = hit[metadata].strip()
        
        ## Get all links and citations
        citation_hrefs = citation_links(db, config, hit)
        current_citation_length = len(metadata_fields['author']) + 2 + len(metadata_fields['title'])
        
        ## Find smallest citation
        if shortest_citation_len == 0:
            shortest_citation_len = current_citation_length
        elif shortest_citation_len > current_citation_length:
            shortest_citation_len = current_citation_length
            
        ## Determine length of text needed
        byte_distance = hit.bytes[-1] - hit.bytes[0]
        length = length/2 + byte_distance + length/2
            
        ## Get concordance and align it
        bytes, byte_start = adjust_bytes(hit.bytes, length)
        conc_text = f.get_text(hit, byte_start, length, config.db_path)
        conc_text = format_strip(conc_text, bytes)
        conc_text = KWIC_formatter(conc_text, len(hit.bytes))
            
        kwic_results.append((citation_hrefs, conc_text, hit, metadata_fields))
    
    if default_short_citation_len > shortest_citation_len:
        shortest_citation_len = default_short_citation_len
    
    ## Populate Kwic_results with bibliography    
    for pos, result in enumerate(kwic_results):
        hrefs, text, hit, metadata_fields = result
        biblio, short_biblio = kwic_citation(shortest_citation_len, metadata_fields, hit[link_to_hit])
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
    full_citation += ', %s' % hit.head
    short_citation.append(hit.head)
        
    if len(', '.join([s for s in short_citation if s])) > short_citation_length:
        short_author, short_title, head = tuple(short_citation)
        if len(short_author) > 10:
            short_author = short_author[:10] + "&#8230;"
            short_citation[0] = short_author
        title_len = short_citation_length - len(short_author)
        if len(short_title) > title_len:
            short_citation[1] = short_title[:title_len]
    short_citation = ', '.join([s for s in short_citation if s])
    
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

if __name__ == "__main__":
    CGIHandler().run(kwic)