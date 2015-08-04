#!/usr/bin/env python

import sys
import timeit
from operator import itemgetter
from philologic.DB import DB
from philologic.HitWrapper import ObjectWrapper
sys.path.append('..')
from functions.wsgi_handler import WSGIHandler
from wsgiref.handlers import CGIHandler
import reports as r
import functions as f
from functions.ObjectFormatter import format_strip, convert_entities, adjust_bytes
try:
    import simplejson as json
except ImportError:
    import json


def get_neighboring_words(environ,start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)

    try:
        index = int(request.hits_done)
    except:
        index = 0
        
    max_time = int(request.max_time)
    
    kwic_words = []
    row_ids = []
    start_time = timeit.default_timer()
    hits = db.query(request["q"],request["method"],request["arg"],**request.metadata)
    c = db.dbh.cursor()
    
    for hit in hits[index:]:
        word_id = ' '.join([str(i) for i in hit.philo_id])
        doc_id = str(hit.philo_id[0])
        query = 'select rowid, philo_name, parent from words where philo_id="%s" limit 1' % word_id
        c.execute(query)
        results = c.fetchone()
        
        hit_word = results['philo_name']
        parent_sentence = results['parent']
        
        if request.direction == "left":
            c.execute('select philo_name, philo_id from words where parent=? and rowid < ?', (parent_sentence, results['rowid']))
            string = []
            for i in c.fetchall():
                string.append(i['philo_name'].decode('utf-8'))
            string.reverse()
            string = ' '.join(string)
        elif request.direction == "right":
            c.execute('select philo_name, philo_id from words where parent=? and rowid > ?', (parent_sentence, results['rowid']))
            string = []
            for i in c.fetchall():
                string.append(i['philo_name'].decode('utf-8'))
            string = ' '.join(string)
        else:
            string = ""
        
        metadata_fields = {}
        for metadata in config.kwic_metadata_sorting_fields:
            metadata_fields[metadata] = hit[metadata].lower()
        
        kwic_words.append((string, index, metadata_fields))
        
        index += 1
        
        elapsed = timeit.default_timer() - start_time
        if elapsed > max_time: # avoid timeouts by splitting the query if more than 10 seconds has been spent in the loop
            break
    
    yield json.dumps({"results": kwic_words, "hits_done": index})


if __name__ == "__main__":
    CGIHandler().run(get_neighboring_words)