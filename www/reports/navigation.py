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
    if has_pages(obj, db):
        page_num = get_page_num(obj,db)
        page_text = f.get_page_text(db, obj.philo_id[0], page_num, obj.filename, path, '')
        if page_text:  ## In case the page does not contain any text
            prev_page, next_page = get_neighboring_pages(db, obj.philo_id[0], page_num)
            return render_template(obj=obj,page_text=page_text,prev_page=prev_page,next_page=next_page,
                                    dbname=dbname,current_page=page_num,f=f,navigate_doc=navigate_doc,
                                    db=db,q=q,template_name='pages.mako')
    obj_text = f.get_text_obj(obj, query_args=q['byte'])
    obj_text = obj_pager(db, obj_text)
    return render_template(obj=obj,philo_id=obj.philo_id[0],dbname=dbname,f=f,navigate_doc=navigate_doc,
                       db=db,q=q,obj_text=obj_text,template_name='object.mako')

def navigate_doc(obj, db):
    conn = db.dbh 
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

def has_pages(obj, db):
    conn = db.dbh
    c = conn.cursor()
    ## this query will be slow until we create a doc id field
    c.execute('select n from pages where philo_id like ?', (str(obj.philo_id[0]) + ' %', ))
    if c.fetchall(): ## This document has pages
        return True
    else:
        return False
    
def get_page_num(obj, db):
    philo_id = ' '.join([str(i) for i in obj.philo_id])
    conn = db.dbh
    c = conn.cursor()
    c.execute('select page from toms where philo_id = ?', (philo_id,))
    return str(c.fetchone()[0] + 1)

def obj_pager(db, obj_text, word_num=500):
    pages =[]
    token_regex = db.locals['punct_regex'] + '|' + db.locals['word_regex']
    words = [i for i in re.split(token_regex, obj_text) if i]
    page = []
    for w in words:
        page.append(w)
        if len(page) > word_num:
            if re.match(db.locals['punct_regex'], w):    
                page = ''.join(page)
                pages.append(page)
                page = []
    if len(page):
        pages.append(''.join(page))
    page_divs = ''
    page_divs += '<div>%s</div>' % pages[0]
    for p in pages[1:]:
        page_divs += "<div style='display:none;'>" + p + '</div>'
    return page_divs
