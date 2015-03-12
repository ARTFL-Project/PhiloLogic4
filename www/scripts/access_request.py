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
    access, user_exists = check_login(config, request)
    if access:
        write_access = open("/tmp/philo4_access", "a")
        print >> write_access, environ["REMOTE_ADDR"]
        yield json.dumps('authorized')
    else:
        yield json.dumps('unauthorized')

def check_login(config, request):
    password_file = open(config.db_path + "/data/logins.txt")
    access = False
    user_exists = False
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
    return access, user_exists

if __name__ == "__main__":
	CGIHandler().run(access_request)
	
