#!/usr/bin/env python

import os
import sys
sys.path.append('..')
import functions as f
import reports as r
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
        citation_hrefs = f.citation_links(db, config, hit)
        metadata_fields = {}
        for metadata in db.locals['metadata_fields']:
            metadata_fields[metadata] = hit[metadata]
        if hit.type == "doc":
            citation = biblio_citation(citation_hrefs, metadata_fields)
        else:
            citation = r.concordance_citation(hit, citation_hrefs, metadata_fields)
        results.append({'citation': citation, 'citation_links': citation_hrefs, 'philo_id': hit.philo_id, "metadata_fields": metadata_fields})
    bibliography_object["results"] = results
    bibliography_object['results_len'] = len(hits)
    bibliography_object['query_done'] = hit.done
    return bibliography_object, hits        
    
def biblio_citation(citation_hrefs, metadata_fields):
    """ Returns a representation of a PhiloLogic object suitable for a bibliographic report. """
    if metadata_fields['author']:
        record = u"%s, <i><a href='%s'>%s</a></i>" % (metadata_fields['author'], citation_hrefs['doc'], metadata_fields['title'])
    else:
        record = u"<i><a href='%s'>%s</a></i>" % (citation_hrefs['doc'],metadata_fields['title'])
    more_metadata = []
    if "pub_place" in metadata_fields and metadata_fields['pub_place']:
        more_metadata.append(metadata_fields['pub_place'])
    if "publisher" in metadata_fields and metadata_fields['publisher']:
        more_metadata.append(metadata_fields['publisher'])
    if "collection" in metadata_fields and metadata_fields['collection']:
        more_metadata.append(metadata_fields['collection'])
    if "date" in metadata_fields and metadata_fields['date']:
        date = metadata_fields['date']
        try:
            date = str(date)
            more_metadata.append(date)
        except:
            pass
    if more_metadata:
        record += '(%s)' % ' '.join(more_metadata)
    if "genre" in metadata_fields and metadata_fields['genre']:
        record += ' [genre: %s]' % metadata_fields['genre']
    return record