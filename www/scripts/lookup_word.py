#!/usr/bin/env python

import os
import sys
import urlparse
import cgi
import json
import sqlite3
sys.path.append('..')
#from functions.wsgi_handler import WSGIHandler
from philologic.DB import DB
from philologic.HitWrapper import ObjectWrapper
from wsgiref.handlers import CGIHandler

def lookup_word_service(environ,start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    cursor = db.dhb.cursor()    

    yield lookup_word(cursor, request.token, request.token_n, request.byte_start, request.byte_end, request.filename)

def lookup_word(cursor,token,n,start,end,filename):
    i = 0
    query = "select * from words where byte_start >= %s and byte_end <= %s and filename = '%s';" % (start, end, filename)
    print >> sys.stderr, query
    cursor.execute(query)
    for row in cursor.fetchall():
        print >> sys.stderr, row['philo_name'], type(row['philo_name'])
        if row['philo_name'] == token:
            print >> sys.stderr, "MATCH", i
            if i == int(n):
                return json.dumps( {"philo_id":row['philo_id'],
                                   "token":row['philo_name'], 
                                   "lemma":row['lemma'],
                                   "pos":row['pos']})
            else:
                i += 1

if __name__ == "__main__":
    if len(sys.argv) > 6:
        db = DB(sys.argv[1])
        print >> sys.stderr, db.dbh
        cursor = db.dbh.cursor()
        lookup_word(cursor,sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
    else:
        CGIHandler.run(lookup_word_service)

