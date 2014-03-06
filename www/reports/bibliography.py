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
        hits = fetch_bibliography(f,path, db, dbname,q,environ)
        if q["group_by_author"]:
            formatted_results = group_by_author(hits, db)
        else:
            formatted_results = [{"citation": f.cite.make_abs_doc_cite_mobile(db,i)} for i in hits]
        return json.dumps(formatted_results)
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
        return render_template(results=hits,db=db,dbname=dbname,q=q, template_name='bibliography.mako',
                           results_per_page=q['results_per_page'], f=f, javascript="bibliography.js", report="bibliography")
    
def group_by_author(hits, db, author="author"):
    object_level = db.locals['default_object_level']
    grouped_results = {}
    for hit in hits:
        author_name = hit[object_level][author]
        if author_name not in grouped_results:
            grouped_results[author_name] = []
        grouped_results[author_name].append({'title': hit[object_level]['title'], 'philo_id': hit[object_level].philo_id})
    return grouped_results        
    
    

