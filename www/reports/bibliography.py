#!/usr/bin/env python

import os
import sys
sys.path.append('..')
import functions as f
import reports as r
from philologic.DB import DB
from wsgiref.handlers import CGIHandler
from functions.wsgi_handler import WSGIHandler
from concordance import citation_links
try:
    import simplejson as json
except ImportError:
    print >> sys.stderr, "Please install simplejson for better performance"
    import json


def bibliography(environ, start_response):
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response('200 OK',headers)
    bibliography_object, hits = bibliography_results(db, request, config)
    yield json.dumps(bibliography_object)
    
def bibliography_results(db, q, config):
    if q.no_metadata:
        hits = db.get_all(db.locals['default_object_level'])
    else:
        hits = db.query(**q.metadata)
    start, end, n = f.link.page_interval(q.results_per_page, hits, q.start, q.end)
    bibliography_object = {"description": {"start": start, "end": end, "n": n, "results_per_page": q.results_per_page},
                          "query": dict([i for i in q])}
    results = []
    result_type = 'doc'
    for hit in hits[start - 1:end]:
        citation_hrefs = citation_links(db, config, hit)
        metadata_fields = {}
        for metadata in db.locals['metadata_fields']:
            metadata_fields[metadata] = hit[metadata]
        result_type = hit.type
        if hit.type == "doc":
            citation = biblio_citation(hit, citation_hrefs)
        else:
            citation = r.concordance_citation(hit, citation_hrefs)
        results.append({'citation': citation, 'citation_links': citation_hrefs, 'philo_id': hit.philo_id, "metadata_fields": metadata_fields})
    bibliography_object["results"] = results
    bibliography_object['results_length'] = len(hits)
    bibliography_object['query_done'] = hits.done
    bibliography_object['result_type'] = result_type
    return bibliography_object, hits        
    
def biblio_citation(hit, citation_hrefs):
    """ Returns a representation of a PhiloLogic object suitable for a bibliographic report. """
    
    citation = {}
    citation['title'] = {'href': citation_hrefs['doc'] + '/table-of-contents', 'label': hit.title.strip()}
    if hit.author:
        citation['author'] = {'href': '', 'label': hit.author.strip()}
    else:
        citation['author'] = {}
    if hit.date:
        citation['date'] = {'href': '', 'label': hit.date.strip()}
    else:
        citation["date"] = {}
        
    ## Div level metadata // Copied from concordance citations
    div1_name = hit.div1.head
    if not div1_name:
        if hit.div1.philo_name == "__philo_virtual":
            div1_name = "Section"
        else:
            if hit.div1["type"] and hit.div1["n"]:
                div1_name = hit.div1['type'] + " " + hit.div1["n"]                       
            else:
                div1_name = hit.div1["head"] or hit.div1['type'] or hit.div1['philo_name'] or hit.div1['philo_type']
    div1_name = div1_name[0].upper() + div1_name[1:]
    
    ## Remove leading/trailing spaces
    div1_name = div1_name.strip()
    div2_name = hit.div2.head.strip()
    div3_name = hit.div3.head.strip()
    
    if div1_name:
        citation['div1'] = {"href": citation_hrefs['div1'], "label": div1_name}
    else:
        citation['div1'] = {}
    if div2_name:
        citation['div2'] = {"href": citation_hrefs['div2'], "label": div2_name}
    else:
        citation['div2'] = {}
    if div3_name:
        citation['div3'] = {"href": citation_hrefs['div3'], "label": div3_name}
    else:
        citation['div3'] = {}
        
    ## Paragraph level metadata
    if "para" in citation_hrefs:
        try:
            citation['para'] = {"href": citation_hrefs['para'], "label": hit.who.strip()}
        except KeyError: ## no who keyword
            citation['para'] = {}

    page_obj = hit.page
    if page_obj['n']:
        page_n = '[page %s]' % page_obj['n']
        citation['page'] = {"href": "", "label": page_n}
    else:
        citation['page'] =  {}
    
    more_metadata = []
    if hit.pub_place:
        more_metadata.append(hit.pub_place.strip())
    if hit.publisher:
        more_metadata.append(hit.publisher.strip())
    if hit.collection:
        more_metadata.append(hit.collection.strip())
    if more_metadata:
        citation['more'] =  '(%s)' % ' '.join([i for i in more_metadata if i])
    else:
        citation['more'] =  ''
    if hit.genre:
        citation['genre'] = '[genre: %s]' % hit.genre
    else:
        citation['genre'] = ''
    return citation

if __name__ == "__main__":
    CGIHandler().run(bibliography)