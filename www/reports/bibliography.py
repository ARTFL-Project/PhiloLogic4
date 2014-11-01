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
    if q["no_q"]:
        hits = db.get_all(db.locals['default_object_level'])
    else:
        hits = db.query(**q["metadata"])
    if q['format'] == "json":
        return hits
    else:
        config = f.WebConfig()
        biblio_criteria = f.biblio_criteria(q, config)
        resource = f.webResources("bibliography", debug=db.locals["debug"])
        return render_template(results=hits,db=db,dbname=dbname,q=q, template_name='bibliography.mako',
                           results_per_page=q['results_per_page'], f=f, biblio_criteria=biblio_criteria,
                           config=config, report="bibliography", css=resource.css, js=resource.js)
    
    

