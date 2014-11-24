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
from functions.wsgi_handler import WSGIHandler
from philologic.DB import DB
from philologic.HitWrapper import ObjectWrapper
from wsgiref.handlers import CGIHandler
from collections import defaultdict



object_depth = {"doc": 1, "div1": 2, "div2": 3, "div3": 4, "para": 5}

def landing_page_content(environ,start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    content_type = request.landing_page_content_type
    q_range = request.range.lower().split('-')
    if content_type != "year":
        letter_range = set([chr(i) for i in range(ord(q_range[0]),ord(q_range[1])+1)])
    c = db.dbh.cursor()
    content = ''
    if content_type == "author":
        content = generate_author_list(c, letter_range, db, config)
    elif content_type == "title":
        content = generate_title_list(c, letter_range, db, config)
    elif content_type == "year":
        content = generate_year_list(c, q_range, db, config)
    yield json.dumps(content)
    
def generate_author_list(c, letter_range, db, config):
    c.execute('select distinct author, count(*) from toms where philo_type="doc" group by author order by author')
    content = []
    for author, count in c.fetchall():
        if not author:
            author = "Unknown"
        if author[0].lower() not in letter_range:
            continue
        if author != "Unknown":
            link = f.link.make_query_link('', author='"' + author + '"')
        else:
            link = f.link.make_query_link('', author='NULL')
        cite = '<a href="%s">%s</a> (%d)' % (link, author, count)
        content.append({"author": author, "cite": cite})
    return content

def generate_title_list(c, letter_range, db, config):
    c.execute('select * from toms where philo_type="doc" order by title')
    content = []
    for i in c.fetchall():
        title = i['title']
        if title[0].lower() not in letter_range:
            continue
        try:
            author = i["author"] or "Anonymous"
        except:
            author = ""
        link = "dispatcher.py/" + i['philo_id'].split()[0]
        cite = '<a href="%s">%s</a> (%s)' % (link, title, author)
        content.append({"title": title, "cite": cite})
    return content

def generate_year_list(c, q_range, db, config):
    low_range = int(q_range[0])
    high_range = int(q_range[1])
    query = 'select * from toms where philo_type="doc" and date >= "%d" and date <= "%d" order by date' % (low_range, high_range)
    c.execute(query)
    content = []
    for i in c.fetchall():
        author = i['author'] or "Anonymous"
        link = "dispatcher.py/" + i['philo_id'].split()[0]
        try:
            date = i['date']
        except:
            date = ""
        cite = '<a href="%s">%s</a> (%s)' % (link, i["title"], author)
        content.append({"cite": cite, "year": date})
    return content


if __name__ == "__main__":
    CGIHandler().run(landing_page_content)
