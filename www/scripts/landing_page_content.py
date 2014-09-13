#!/usr/bin/env python

import os
import sys
import urlparse
import cgi
import json
import sqlite3
sys.path.append('..')
import reports as r
import functions as f
from functions.wsgi_handler import parse_cgi
from philologic.HitWrapper import ObjectWrapper
from wsgiref.handlers import CGIHandler
from collections import defaultdict



object_depth = {"doc": 1, "div1": 2, "div2": 3, "div3": 4, "para": 5}

def landing_page_content(environ,start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    environ["SCRIPT_FILENAME"] = environ["SCRIPT_FILENAME"].replace('scripts/landing_page_content.py', '')
    cgi = urlparse.parse_qs(environ["QUERY_STRING"],keep_blank_values=True)
    content_type = cgi.get('landing_page_content_type',[])[0]
    q_range = cgi.get('range',[])[0].lower().split('-')
    if content_type != "year":
        letter_range = set([chr(i) for i in range(ord(q_range[0]),ord(q_range[1])+1)])
    db, path_components, q = parse_cgi(environ)
    c = db.dbh.cursor()
    content = ''
    if content_type == "author":
        content = generate_author_list(c, letter_range)
    elif content_type == "title":
        content = generate_title_list(c, letter_range)
    elif content_type == "year":
        content = generate_year_list(c, q_range)
    yield json.dumps(content)
    
def generate_author_list(c, letter_range):
    c.execute('select distinct author, count(*) from toms where philo_type="doc" group by author order by author')
    content = []
    for author, count in c.fetchall():
        if author == None:
            author = "Anonymous"
        if author[0].lower() not in letter_range:
            continue
        link = f.link.make_query_link('', author='"' + author + '"')
        content.append({"author": author, "count": count, "link": link})
    return content

def generate_title_list(c, letter_range):
    c.execute('select title, author, philo_id from toms where philo_type="doc" order by title')
    content = []
    for title, author, philo_id in c.fetchall():
        if title[0].lower() not in letter_range:
            continue
        author = author or "Anonymous"
        link = "dispatcher.py/" + philo_id.split()[0]
        content.append({"title": title, "author": author, "link": link})
    return content

def generate_year_list(c, q_range):
    low_range = int(q_range[0])
    high_range = int(q_range[1])
    query = 'select title, author, date, philo_id from toms where philo_type="doc" and date >= "%d" and date <= "%d" order by date' % (low_range, high_range)
    c.execute(query)
    content = []
    for title, author, date, philo_id in c.fetchall():
        author = author or "Anonymous"
        link = "dispatcher.py/" + philo_id.split()[0]
        content.append({"title": title, "author": author, "year": date, "link": link})
    return content


if __name__ == "__main__":
    CGIHandler().run(landing_page_content)
