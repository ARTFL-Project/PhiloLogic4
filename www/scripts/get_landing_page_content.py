#!/usr/bin/env python

import os
import sys
import urlparse
import cgi
import json
import sqlite3
import re
import unicodedata
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
    if content_type != "date":
        letter_range = set([chr(i) for i in range(ord(q_range[0]),ord(q_range[1])+1)])
    c = db.dbh.cursor()
    content = ''
    if content_type == "author":
        content = generate_author_list(c, letter_range, db, config, request)
    elif content_type == "title":
        content = generate_title_list(c, letter_range, db, config, request)
    elif content_type == "date":
        content = generate_year_list(c, q_range, db, config, request)
    yield json.dumps(content)
    
def generate_author_list(c, letter_range, db, config, request):
    c.execute('select distinct author, count(*) from toms where philo_type="doc" group by author order by author')
    content = []
    for author, count in c.fetchall():
        if not author:
            author = "Unknown"
        if author[0].lower() not in letter_range:
            continue
        if author != "Unknown":
            url = 'query?report=bibliography&author="%s"' % author
        else:
            url = 'query?report=bibliography&author=NULL'
        content.append({"author": author, "url": url, "count": count, "initial": author.decode('utf-8')[0]})
    return content

def generate_title_list(c, letter_range, db, config, request):
    c.execute('select * from toms where philo_type="doc"')
    content = []
    try:
        prefixes =  '|'.join([i for i in config.title_prefix_removal])
    except: # for backwards compatibility
        prefixes = ""
    prefix_sub = re.compile(r"^%s" % prefixes, re.I|re.U)
    for i in c.fetchall():
        title = i['title'].decode('utf-8').lower()
        title = prefix_sub.sub('', title).strip()
        if title[0].lower() not in letter_range:
            continue
        try:
            author = i["author"] or "Anonymous"
        except:
            author = ""
        url = "navigate/%s/table-of-contents" % i['philo_id'].split()[0]
        # Smash accents and normalize for sorting
        title = ''.join([j for j in unicodedata.normalize("NFKD",title) if not unicodedata.combining(j)])
        content.append({"title": i['title'], "url": url, "author": author, "initial": title[0].upper(), 'truncated': title})
    content = sorted(content, key=lambda x: x['truncated'])
    return content

def generate_year_list(c, q_range, db, config, request):
    low_range = int(q_range[0])
    high_range = int(q_range[1])
    query = 'select * from toms where philo_type="doc" and date >= "%d" and date <= "%d" order by date' % (low_range, high_range)
    c.execute(query)
    content = []
    for i in c.fetchall():
        author = i['author'] or "Anonymous"
        url = "navigate/%s/table-of-contents" % i['philo_id'].split()[0]
        try:
            date = i['date']
        except:
            date = ""
        content.append({"title": i['title'], "url": url, "date": date, "author": author, "initial": date})
    return content


if __name__ == "__main__":
    CGIHandler().run(landing_page_content)
