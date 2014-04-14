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
        if q["group_by_author"]:
            wrapper = group_by_author(hits, db)
        else:
            for i in hits[0:100]:
                full_metadata = {}
                for metadata in db.locals['metadata_fields']:
                    full_metadata[metadata] = i[metadata]
                full_metadata['philo_id'] = ' '.join([str(j) for j in i.philo_id])
                wrapper.append(full_metadata)
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
        biblio_criteria = []
        for k,v in q["metadata"].iteritems():
            if v:
                close_icon = '<span class="ui-icon ui-icon-circle-close remove_metadata" data-metadata="%s"></span>' % k
                biblio_criteria.append('<span class="biblio_criteria">%s: <b>%s</b> %s</span>' % (k.title(), v.decode('utf-8', 'ignore'), close_icon))
        biblio_criteria = ' '.join(biblio_criteria)
        return render_template(results=hits,db=db,dbname=dbname,q=q, template_name='bibliography.mako',
                           results_per_page=q['results_per_page'], f=f, biblio_criteria=biblio_criteria,
                           report="bibliography")
    
def group_by_author(hits, db, author="author"):
    object_level = db.locals['default_object_level']
    grouped_results = {}
    for hit in hits:
        author_name = hit[object_level][author].strip()
        if author_name == '':
            author_name = "Anonymous"
        if author_name not in grouped_results:
            grouped_results[author_name] = []
        grouped_results[author_name].append({'title': hit[object_level]['title'], 'philo_id': hit[object_level].philo_id})
    return sorted(grouped_results.iteritems(), key=lambda x: x[0])
    
    

