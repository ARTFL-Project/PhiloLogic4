#!/usr/bin/env python

from __future__ import division
import timeit
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
    
    input_object = json.loads(environ['wsgi.input'].read())
    frequencies = input_object['results']
    hits_done = input_object['hits_done']
    start_time = timeit.default_timer()
    count = 0
    sorted_frequencies = sorted(frequencies.iteritems(), key= lambda x: x[0])
    
    for label, m in sorted_frequencies[hits_done:]:
        args = []
        query_metadata = {}
        for metadata in m['metadata']:
            if m['metadata'][metadata] and metadata != "date" and m['metadata'][metadata] != "NULL":
                if not m['metadata'][metadata].startswith('"'):
                    query_metadata[metadata] = '"%s"' % m['metadata'][metadata].encode('utf-8')
                else:
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
        hits_done += 1
        elapsed = timeit.default_timer() - start_time
        if elapsed > 10: # avoid timeouts by splitting the query if more than 10 seconds has been spent in the loop
            break
    
    if len(sorted_frequencies) > hits_done:
        more_results = True
    else:
        more_results = False
        
    yield json.dumps({"frequencies": dict(sorted_frequencies[:hits_done]),
                      "more_results": more_results,
                      "hits_done": hits_done})
    

if __name__ == "__main__":
    CGIHandler().run(get_metadata_token_count)
