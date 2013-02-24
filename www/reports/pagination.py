#!/usr/bin/env python

import sys
sys.path.append('..')
import os
import functions as f
from functions.wsgi_handler import wsgi_response
from render_template import render_template

def pagination(environ,start_response):
    db, dbname, path_components, q = wsgi_response(environ,start_response)
    path = os.getcwd().replace('functions/', '')
    doc_page = q['doc_page']
    philo_id = q['philo_id']
    filename = q['filename']
    bytes = q['byte']
    page_text = f.get_page_text(db, philo_id, doc_page, filename, path, bytes)
    prev_page, next_page = get_neighboring_pages(db, philo_id, doc_page)
    return render_template(page_text=page_text,db=db,dbname=dbname,current_page=doc_page,
                           prev_page=prev_page,next_page=next_page,pagination=pagination,
                           filename=filename, philo_id=philo_id,bytes=bytes,template_name="doc_page.mako")

def get_neighboring_pages(db, philo_id, doc_page):
    conn = db.dbh
    c = conn.cursor()
    if doc_page != '1':
        prev_page = int(doc_page) - 1
    else:
        prev_page = None
    next_page = str(int(doc_page) + 1)
    c.execute('select n from pages where n=?', (next_page,))
    if c.fetchone() == None:
        next_page = None
    return prev_page, next_page
    