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
        obj_text = f.get_text_obj(obj, path, query_args=q['byte'])
        return json.dumps({'text': obj_text, 'prev': prev, 'next': next})
    if obj.philo_type == 'doc':
        return render_template(obj=obj,philo_id=obj.philo_id[0],dbname=dbname,f=f,navigate_doc=navigate_doc,
                       db=db,q=q,config=config,template_name='t_o_c.mako', report="t_o_c")
    obj_text = f.get_text_obj(obj, path, query_args=q['byte'])
    return render_template(obj=obj,philo_id=obj.philo_id[0],dbname=dbname,f=f,navigate_doc=navigate_doc,
                       db=db,q=q,obj_text=obj_text,prev=prev,next=next,config=config,generate_ajax_scripts=generate_ajax_scripts,
                       template_name='object.mako', report="navigation")

def generate_ajax_scripts(config, philo_id):
    script = config.db_url + '/scripts/go_to_obj.py?philo_id=' + philo_id
    return script


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
        c.execute("select philo_id, philo_name, philo_type, head from toms where rowid between ? and ? and philo_name!='__philo_virtual' and  philo_type>='div' and philo_type<='div3'", (start_rowid, end_rowid))
    except sqlite3.OperationalError:
        c.execute("select philo_id, philo_name, philo_type from toms where rowid between ? and ? and philo_name!='__philo_virtual' and  philo_type>='div' and philo_type<='div3'", (start_rowid, end_rowid))
    text_hierarchy = []
    for i in c.fetchall():
        if i['philo_name'] == '__philo_virtual':
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