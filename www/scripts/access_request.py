#! /usr/bin/env python

import os
import sys
import sqlite3
sys.path.append('..')
import functions as f
from functions.wsgi_handler import WSGIHandler
from philologic.DB import DB
from cgi import FieldStorage
from wsgiref.handlers import CGIHandler
from ast import literal_eval as eval
import json


default_reports = ['concordance', 'kwic', 'collocation', 'time_series', 'navigation']


def access_request(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'), ("Access-Control-Allow-Origin", "*")]
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    if request.authenticated:
        access = True
    else:
        if request.username and request.password:
            access = check_login(config, request)
            if access:
                incoming_address = environ['REMOTE_ADDR']
                token = f.make_token(incoming_address, db)
                if token:
                    h, ts = token
                    headers.append( ("Set-Cookie", "hash=%s" % h) )
                    headers.append( ("Set-Cookie", "timestamp=%s" % ts) )
        else:
            access = False
    start_response(status, headers)
    if access:
        yield json.dumps({'access': True})
    else:
        yield json.dumps({'access': False})


def check_login(config, request):
    try:
        password_file = open(config.db_path + "/data/logins.txt")
    except IOError:
        return (True, default_reports)
    access = False
    for line in password_file:
        fields = line.strip().split('\t')
        user = fields[0]
        passwd = fields[1]
        if user == request.username:
            if passwd == request.password:
                access = True
                break
            else:
                access = False
                break
    return access

if __name__ == "__main__":
    CGIHandler().run(access_request)
