#!/usr/bin/env python

import os
import sys
import urlparse
sys.path.append('..')
from functions.wsgi_handler import WSGIHandler
from wsgiref.handlers import CGIHandler
from philologic.DB import DB
import reports as r
import functions as f
import cgi
import json

object_levels = set(["doc", "div1", "div2", "div3"])

def get_bibliography(environ,start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    object_level = request.object_level
    if object_level and object_level in object_levels:
        hits = db.get_all(object_level)
    else:
        hits = db.get_all(db.locals['default_object_level'])
    results = []
    c = db.dbh.cursor()
    for hit in hits:
        hit_object = {}
        for field in db.locals['metadata_fields']:
            hit_object[field] = hit[field] or ''
        if object_level == "doc":
            hit_object['philo_id'] = hit.philo_id[0]
        else:
            hit_object['philo_id'] = '/'.join([str(i) for i in hit.philo_id])
        doc_id = str(hit.philo_id[0]) + ' 0 0 0 0 0 0'
        next_doc_id = str(hit.philo_id[0] + 1) + ' 0 0 0 0 0 0'
        c.execute('select rowid from toms where philo_id="%s"' % doc_id)
        doc_row = c.fetchone()['rowid']
        c.execute('select rowid from toms where philo_id="%s"' % next_doc_id)
        try:
            next_doc_row = c.fetchone()['rowid']
        except TypeError: # if this is the last doc, just get the last rowid in the table.
            c.execute('select max(rowid) from toms;')
            next_doc_row = c.fetchone()[0]
        c.execute('select head from toms where rowid between %d and %d and head is not null limit 1' % (doc_row, next_doc_row))
        try:
            start_head = c.fetchone()['head']
            start_head = start_head.decode('utf-8').lower().title().encode('utf-8')
        except:
            start_head = ''
        c.execute('select head from toms where rowid between %d and %d and head is not null order by rowid desc limit 1' % (doc_row, next_doc_row))
        try:
            end_head = c.fetchone()['head']
            end_head = end_head.decode('utf-8').lower().title().encode('utf-8')
        except:
            end_head = ''
        hit_object['start_head'] = start_head
        hit_object['end_head'] = end_head
        
        results.append(hit_object)
    
    yield json.dumps(results)

if __name__ == "__main__":
    CGIHandler().run(get_bibliography)