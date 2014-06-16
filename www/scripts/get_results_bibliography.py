#!/usr/bin/env python

import os
import sys
import urlparse
import cgi
import json
import sqlite3
sys.path.append('..')
import reports as r
import functions as f
from functions.wsgi_handler import parse_cgi
from philologic.HitWrapper import ObjectWrapper
from wsgiref.handlers import CGIHandler



object_depth = {"doc": 1, "div1": 2, "div2": 3, "div3": 4, "para": 5}

def get_results_bibliography(environ,start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    environ["SCRIPT_FILENAME"] = environ["SCRIPT_FILENAME"].replace('scripts/get_results_bibliography.py', '')
    cgi = urlparse.parse_qs(environ["QUERY_STRING"],keep_blank_values=True)
    philo_ids = cgi.get('philo_id',[])
    db, path_components, q = parse_cgi(environ)
    obj_level = db.locals["default_object_level"]
    path = db.locals['db_path']
    path = path[:path.rfind("/data")]
    config = f.WebConfig()
    c = db.dbh.cursor()
    citations = []
    citation_counter = {}
    for philo_id in philo_ids:
        obj = ObjectWrapper(philo_id.split()[:7], db)
        obj.bytes = []
        citation = f.cite.biblio_citation(db, config, obj)
        if citation not in citation_counter:
            citations.append(citation)
            citation_counter[citation] = 1
        else:
            citation_counter[citation] += 1
    citations_with_count = []
    for cite in citations:
        count = citation_counter[cite]
        citations_with_count.append([cite, count])
    yield json.dumps(citations_with_count)

if __name__ == "__main__":
    CGIHandler().run(get_results_bibliography)
