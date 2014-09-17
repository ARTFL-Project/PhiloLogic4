#! /usr/bin/env python

import os
import sys
import sqlite3
sys.path.append('..')
from functions.wsgi_handler import parse_cgi
from cgi import FieldStorage
from wsgiref.handlers import CGIHandler
import json


def check_login(path, username, password):
    password_file = open(path + "/data/user_pass")
    access = False
    user_exists = False
    for line in password_file:
        user, passwd = tuple(line.strip().split())
        if user == username:
            print >> sys.stderr, "FOUND YOU", user, passwd, password
            user_exists = True
            if passwd == password:
                access = True
                break
            else:
                access = False
                break
    return access, user_exists
    

def password_entry(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    form = FieldStorage()
    username = form.getvalue('username')
    password = form.getvalue('password')
    print >> sys.stderr, "PASSWORD", password
    path = environ["SCRIPT_FILENAME"].replace('scripts/password_entry.py', '')  
    access, user_exists = check_login(path, username, password)
    if access:
        write_access = open("/tmp/philo4_access", "a")
        print >> write_access, environ["REMOTE_ADDR"]
        yield json.dumps('ok')
    else:
        yield json.dumps('not')


if __name__ == "__main__":
	CGIHandler().run(password_entry)
	
