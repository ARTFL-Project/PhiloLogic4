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
    #if obj.philo_type == 'doc' and q['doc_page']:
    #    page_text = f.get_page_text(db, obj, q['doc_page'], path, q['byte'])
    #    #page_text = obj.get_page() This does not fetch the right page, just the first page of the object
    #    if page_text:
    #        doc_id = str(obj.philo_id[0]) + ' %'
    #        prev_page, next_page = get_neighboring_pages(db, doc_id, q['doc_page'])    
    #        return render_template(obj=obj,page_text=page_text,prev_page=prev_page,next_page=next_page,
    #                               dbname=dbname,current_page=q['doc_page'],f=f,navigate_doc=navigate_doc,
    #                               db=db,q=q,template_name='pages.mako')
    #    else:
    #        path_components += ['2']
    #        obj = db[path_components]
    #if has_pages(obj, db):
    #    page_num = get_page_num(obj,db)
    #    if page_num:
    #        page_text = f.get_page_text(db, obj, q['doc_page'], path, q['byte'])
    #        if page_text:  ## In case the page does not contain any text
    #            doc_id = str(obj.philo_id[0]) + ' %'
    #            prev_page, next_page = get_neighboring_pages(db, doc_id, page_num)
    #            return render_template(obj=obj,page_text=page_text,prev_page=prev_page,next_page=next_page,
    #                                    dbname=dbname,current_page=page_num,f=f,navigate_doc=navigate_doc,
    #                                    db=db,q=q,template_name='pages.mako')
    if obj.philo_type == 'doc':
        return render_template(obj=obj,philo_id=obj.philo_id[0],dbname=dbname,f=f,navigate_doc=navigate_doc,
                       db=db,q=q,template_name='t_o_c.mako')
    obj_text = f.get_text_obj(obj, path, query_args=q['byte'])
    #obj_text = obj_pager(db, obj, obj_text)  ## this creates virtual pages
    prev = ' '.join(obj.prev.split()[:7])
    next = ' '.join(obj.next.split()[:7])
    return render_template(obj=obj,philo_id=obj.philo_id[0],dbname=dbname,f=f,navigate_doc=navigate_doc,
                       db=db,q=q,obj_text=obj_text,prev=prev,next=next,template_name='object.mako')

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

def obj_pager(db, obj, obj_text, word_num=500):
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
    highlight = False
    highlight_tag = re.compile('class="highlight"')
    for p in pages[1:-1]:
        if highlight_tag.search(p):
            highlight = True
            page_divs += "<div>" + p + '</div>'
        else:
            page_divs += "<div style='display:none;'>" + p + '</div>'
    if highlight:
        page_divs = '<div style="display:none;">%s</div>' % pages[0] + page_divs
    else:
        page_divs = '<div>%s</div>' % pages[0] + page_divs
    next_id = obj.next.split(" ")[:7]
    next_url = f.link.make_absolute_object_link(db, next_id)
    next_link = '<a href="%s">NEXT</a>' % next_url
    page_divs += "<div style='display:none;'>%s%s</div>" % (page[-1], next_link)
    return page_divs
