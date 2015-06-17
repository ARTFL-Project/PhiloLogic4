#!/usr/bin/env python

from __future__ import division
import sys
sys.path.append('..')
from functions.wsgi_handler import WSGIHandler
from philologic.DB import DB
from wsgiref.handlers import CGIHandler
import reports as r
import functions as f
try:
    import simplejson as json
except ImportError:
    import json

def get_metadata_token_count(environ,start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    results = ''
    frequencies = json.loads(environ['wsgi.input'].read())
    word_counts = []
    c = db.dbh.cursor()
    count = 0
    for label, m in frequencies.iteritems():
        args = []
        query_metadata = {}
        for metadata in m['metadata']:
            query_metadata[metadata] = m['metadata'][metadata].encode('utf-8')
        hits = db.query(**query_metadata)
        total_count = 0
        for hit in hits:
            total_count += int(hit['word_count'])
        try:
            frequencies[label]['count'] = round(float(m['count']) / total_count * 1000000, 3)
        except:
            count += 1
            frequencies[label]['count'] = 0    
        
    yield json.dumps(frequencies)
    

if __name__ == "__main__":
    CGIHandler().run(get_metadata_token_count)
