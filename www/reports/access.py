#!/usr/bin/env python

import sys
sys.path.append('..')
import functions as f
import socket
from functions.wsgi_handler import WSGIHandler
from philologic.DB import DB


def access(environ, start_response):
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    incoming_address = environ['REMOTE_ADDR']
    hostname = socket.gethostname()
    headers = [('Content-type', 'text/html; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response('200 OK',headers)
    return ""