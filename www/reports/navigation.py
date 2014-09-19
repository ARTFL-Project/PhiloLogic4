#!/usr/bin/env python

import sys
sys.path.append('..')
import os
import sqlite3
import re
import sys
import functions as f
from functions.wsgi_handler import wsgi_response
from functions import concatenate_files
from render_template import render_template
from philologic import HitWrapper
import json

philo_types = set(['div1', 'div2', 'div3'])

def navigation(environ,start_response):
    db, dbname, path_components, q = wsgi_response(environ,start_response)
    path = os.getcwd().replace('functions/', '')
    obj = db[path_components]
    config = f.WebConfig()
    prev = ' '.join(obj.prev.split()[:7])
    next = ' '.join(obj.next.split()[:7])
    if q['format'] == "json":
        if check_philo_virtual(db, path_components):
            obj = db[path_components[:-1]]
        obj_text = f.get_text_obj(obj, path, query_args=q['byte'])
        return json.dumps({'text': obj_text, 'prev': prev, 'next': next, 'shrtcit':  f.cite.make_abs_doc_shrtcit_mobile(db,obj)})
    if obj.philo_type == 'doc':
        concatenate_files(path, "t_o_c", debug=db.locals["debug"])
        return render_template(obj=obj,philo_id=obj.philo_id[0],dbname=dbname,f=f,navigate_doc=navigate_doc,
                       db=db,q=q,config=config,template_name='t_o_c.mako', report="t_o_c",
                       ressources=f.concatenate.report_files)
    obj_text = f.get_text_obj(obj, path, query_args=q['byte'])
    concatenate_files(path, "navigation", debug=db.locals["debug"])
    return render_template(obj=obj,philo_id=obj.philo_id[0],dbname=dbname,f=f,navigate_doc=navigate_doc,
                       db=db,q=q,obj_text=obj_text,prev=prev,next=next,config=config,
                       template_name='object.mako', report="navigation", ressources=f.concatenate.report_files)

def check_philo_virtual(db, path_components):
    object_type = ''
    if len(path_components) == 2:
        object_type = "div1"
    if len(path_components) == 3:
        object_type = "div2"
    if len(path_components) == 4:
        object_type = "div3"
    c = db.dbh.cursor()
    query = 'select philo_name from toms where philo_id like "' + ' '.join(path_components) + ' %" and philo_type="' + object_type + '"'
    c.execute(query)
    try:
        name = c.fetchone()[0]
        if name == "__philo_virtual":
            return True
        else:
            return False
    except TypeError:
        return False

def navigate_doc(obj, db):
    """This function fetches all philo_ids for div elements within a doc"""
    conn = db.dbh 
    c = conn.cursor()
    doc_id =  int(obj.philo_id[0])
    next_doc_id = doc_id + 1
    c.execute('select rowid from toms where philo_id="%d 0 0 0 0 0 0"' % doc_id)
    start_rowid = c.fetchone()[0]
    c.execute('select rowid from toms where philo_id="%d 0 0 0 0 0 0"' % next_doc_id)
    end_rowid = c.fetchone()[0]
    try:
        c.execute("select philo_id, philo_name, philo_type, head from toms where rowid between ? and ? and philo_type>='div' and philo_type<='div3'", (start_rowid, end_rowid))
    except sqlite3.OperationalError:
        c.execute("select philo_id, philo_name, philo_type from toms where rowid between ? and ? and  philo_type>='div' and philo_type<='div3'", (start_rowid, end_rowid))
    text_hierarchy = []
    for i in c.fetchall():
        if i['philo_name'] == '__philo_virtual' and i["philo_type"] != "div1":
            continue
        else:
            philo_id = i['philo_id']
            philo_type = i['philo_type']
            try:
                head = i['head'].decode('utf-8', 'ignore')
            except:
                head = philo_type
            text_hierarchy.append((philo_id, philo_type, head))
    print >> sys.stderr, "NUM", start_rowid, end_rowid, len(text_hierarchy)
    return text_hierarchy
    
def get_neighboring_pages(db, doc_id, doc_page):
    conn = db.dbh
    c = conn.cursor()
    c.execute('select philo_seq from pages where n=? and philo_id like ?', (doc_page, doc_id))
    philo_seq = c.fetchone()[0]
    prev_seq = philo_seq - 1
    c.execute('select n from pages where philo_seq=? and philo_id like ?', (prev_seq, doc_id))
    try:
        prev_page = c.fetchone()[0]
    except TypeError:  ## There is no previous page in that doc
        prev_page = None
    next_seq = philo_seq + 1
    c.execute('select n from pages where philo_seq=? and philo_id like ?', (next_seq, doc_id))
    try:
        next_page = c.fetchone()[0]
    except TypeError:  ## There is no previous page in that doc
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
    try:
        return str(c.fetchone()[0] + 1)
    except TypeError:
        try:
            return c.fetchone()[0]
        except:
            return None
