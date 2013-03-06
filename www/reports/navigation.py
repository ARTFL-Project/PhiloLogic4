#!/usr/bin/env python

import sys
sys.path.append('..')
import os
import sqlite3
import re
import sys
import functions as f
from functions.wsgi_handler import wsgi_response
from render_template import render_template
from philologic import HitWrapper

philo_types = set(['div1', 'div2', 'div3'])

def navigation(environ,start_response):
    db, dbname, path_components, q = wsgi_response(environ,start_response)
    path = os.getcwd().replace('functions/', '')
    obj = db[path_components]
    if obj.philo_type == 'doc':
        if not q['doc_page']:
            q['doc_page'] = '1'
        page_text = f.get_page_text(db, obj.philo_id[0], q['doc_page'], obj.filename, path, q['byte'])
        if page_text:
            prev_page, next_page = get_neighboring_pages(db, obj.philo_id[0], q['doc_page'])    
            return render_template(obj=obj,page_text=page_text,prev_page=prev_page,next_page=next_page,
                                   dbname=dbname,current_page=q['doc_page'],f=f,navigate_doc=navigate_doc,
                                   db=db,q=q,template_name='pages.mako')
        else:
            path_components += ['2']
            obj = db[path_components]
    obj_text = f.get_text_obj(obj, query_args=q['byte'])
    return render_template(obj=obj,philo_id=obj.philo_id[0],dbname=dbname,f=f,navigate_doc=navigate_doc,
                           db=db,q=q,obj_text=obj_text,template_name='object.mako')

def navigate_doc(obj, db):
    conn = db.dbh ## make this more accessible 
    c = conn.cursor()
    query =  str(obj.philo_id[0]) + " _%"
    c.execute("select philo_id, philo_name, philo_type, byte_start from toms where philo_id like ?", (query,))
    text_hierarchy = []
    for id, philo_name, philo_type, byte in c.fetchall():
        if philo_type not in philo_types or philo_name == '__philo_virtual':
            continue
        else:
            text_hierarchy.append(db[id])
    return text_hierarchy
    
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
