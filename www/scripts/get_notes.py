#!/usr/bin/env python

import os
import sys
sys.path.append('..')
from philologic.DB import DB
from functions.wsgi_handler import WSGIHandler
from wsgiref.handlers import CGIHandler
from philologic.HitWrapper import ObjectWrapper
import functions as f
from reports.navigation import generate_text_object
import json

def get_notes(environ,start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)    
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    path = config.db_path
    target = request.target.replace('#', '')
    try:
        philo_id = db.query(id=target)[0].philo_id
        obj = ObjectWrapper(philo_id, db)
        text_object = generate_text_object(obj, db, request, config)
        yield json.dumps(text_object)
    except IndexError:
        yield json.dumps('')
    

if __name__ == "__main__":
    CGIHandler().run(get_notes)