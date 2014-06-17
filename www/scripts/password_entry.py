#! /usr/bin/env python

import os
import sys
import sqlite3
sys.path.append('..')
from functions.wsgi_handler import parse_cgi
from cgi import FieldStorage
from wsgiref.handlers import CGIHandler
import json

def password_entry(environ, start_response):
	status = '200 OK'
	headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
	start_response(status,headers)
	form = FieldStorage()
	username = form.getvalue('username')
	password = form.getvalue('password')
	environ["SCRIPT_FILENAME"] = environ["SCRIPT_FILENAME"].replace('scripts/password_entry.py', '')
	db, path_components, q = parse_cgi(environ)
	conn = sqlite3.connect(db.locals['db_path'] + '/access.db')
	print >> sys.stderr, 'CONNECTING TO', db.locals['db_path'] + '/access.db'
	c = conn.cursor()
	c.execute('select * from userlogin where username=? and password=?', (username, password))
	if c.fetchone():
		print >> sys.stderr, "SUCCESSFUL LOGIN:  ", username, password
		client_address = environ["REMOTE_ADDR"]
		status_info = "password ip:"+username
		conn.execute('INSERT INTO domain_list(client_address, access_value, status) VALUES (?,?,?);', (client_address,'true',status_info))
		conn.commit()
		conn.close()
		print >> sys.stderr, "UPDATING SQLITE WITH: ", client_address
		yield json.dumps('ok')
	else:
		print >> sys.stderr, "LOGIN ATTEMPT:  ", username, password 
		yield json.dumps('not')
	
	

if __name__ == "__main__":
	CGIHandler().run(password_entry)
	
