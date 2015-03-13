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
import json

def access_request(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    access = check_login(config, request)
    ip_address = environ["REMOTE_ADDR"]
    if access:
        yield json.dumps('authorized')
    else:
        yield json.dumps('unauthorized')

def check_login(config, request):
    password_file = open(config.db_path + "/data/logins.txt")
    access = False
    for line in password_file:
        user, passwd = tuple(line.strip().split())
        if user == request.username:
            user_exists = True
            if passwd == request.password:
                access = True
                break
            else:
                access = False
                break
    return access

if __name__ == "__main__":
	CGIHandler().run(access_request)
	
