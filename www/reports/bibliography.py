#!/usr/bin/env python

import os
import sys
sys.path.append('..')
import functions as f
from functions.wsgi_handler import wsgi_response
from render_template import render_template
import json


def bibliography(environ, start_response):
    db, dbname, path_components, q = wsgi_response(environ,start_response)
    path = os.getcwd().replace('functions/', '')
    if q['format'] == "json":
        wrapper = []
        hits = fetch_bibliography(f,path, db, dbname,q,environ)
        hit_count = len(hits)
        for i in hits[0:100]:
            in_citation = f.cite.make_abs_doc_cite_biblio_mobile(db,i)
            citation, text = in_citation.split('|')
            wrapper.append({'philo_id': i.philo_id, 'citation': citation, 'hit_count': hit_count, 'text': text})
        return json.dumps(wrapper)
    else:
        return fetch_bibliography(f,path, db, dbname,q,environ)

def fetch_bibliography(f,path, db, dbname, q, environ):
    config = f.WebConfig()
    bibliography_object, hits = bibligraphy_results(db, q, config)
    biblio_criteria = f.biblio_criteria(q, config)
    resource = f.webResources("bibliography", debug=db.locals["debug"])
    pages = f.link.generate_page_links(bibliography_object['description']['start'], q['results_per_page'], q, hits)
    return render_template(bibliography=bibliography_object,db=db,dbname=dbname,q=q, template_name='bibliography.mako',
                           pages=pages, biblio_criteria=biblio_criteria,config=config, report="bibliography", css=resource.css, js=resource.js)
    
def bibligraphy_results(db, q, config):
    if q["no_q"]:
        hits = db.get_all(db.locals['default_object_level'])
    else:
        hits = db.query(**q["metadata"])
    start, end, n = f.link.page_interval(q['results_per_page'], hits, q["start"], q["end"])
    bibliography_object = {"description": {"start": start, "end": end, "n": n, "results_per_page": q['results_per_page']},
                          "query": q}
    results = []
    for hit in hits[start - 1:end]:
        if hit.type == "doc":
            citation = f.biblio_citation(db, config, hit)
        else:
            citation = f.concordance_citation(db, config, hit)
        metadata_fields = {}
        for metadata in q['metadata']:
            metadata_fields[metadata] = hit[metadata]
        results.append({'citation': citation, 'philo_id': hit.philo_id, "metadata_fields": metadata_fields})
    bibliography_object["results"] = results
    bibliography_object['results_len'] = len(hits)
    bibliography_object['query_done'] = hit.done
    return bibliography_object, hits        
    
    

