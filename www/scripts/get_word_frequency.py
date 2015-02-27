#!/usr/bin/env python

import os
import sys
import urlparse
sys.path.append('..')
from functions.wsgi_handler import WSGIHandler
from philologic.DB import DB
from wsgiref.handlers import CGIHandler
from reports.word_property_filter import get_word_attrib
import reports as r
import functions as f
import cgi
import json
import sqlite3
import time


def generate_word_frequency(hits,q,db,config):
    """reads through a hitlist. looks up q["field"] in each hit, and builds up a list of 
       unique values and their frequencies."""
    field = q["field"]
    counts = {}
    for n in hits[q.interval_start:q.interval_end]:
#        print >> sys.stderr, "WORDS", repr(n.words)
        key = get_word_attrib(n,field,db)
        if not key:
            key = "NULL" # NULL is a magic value for queries, don't change it recklessly.
        if key not in counts:
            counts[key] = 0
        counts[key] += 1
    
    table = {}
    for k,v in counts.iteritems():
        url = f.link.make_absolute_query_link(config,q,report="word_property_filter",word_property=field,word_property_value=k)
        table[k] = {'count': v, 'url': url}

    return field, table
    

def get_frequency(environ,start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    hits = db.query(request["q"],request["method"],request["arg"],**request.metadata)
    field, results = generate_word_frequency(hits,request,db,config)
    yield json.dumps(results,indent=2)
    return
    
if __name__ == "__main__":
    CGIHandler().run(get_frequency)
