#!/usr/bin/env python

import os
import cgi
import sys
sys.path.append('..')
import functions as f
import json
import subprocess
from wsgiref.handlers import CGIHandler
from philologic.QuerySyntax import parse_query, group_terms
from philologic.Query import split_terms, grep_word, get_expanded_query
from philologic.DB import DB
from functions.wsgi_handler import WSGIHandler


def term_list(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'), ("Access-Control-Allow-Origin","*")]
    start_response(status, headers)
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    q = WSGIHandler(db, environ)
    hits = db.query(q["q"],q["method"],q["arg"],**q.metadata)
    expanded_terms = get_expanded_query(hits)
    yield json.dumps(expanded_terms[0])

if __name__ == "__main__":
    CGIHandler().run(term_list)

