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
from bibliography import biblio_citation
import json

philo_types = set(['div1', 'div2', 'div3'])

def navigation(environ,start_response):
    db, dbname, path_components, q = wsgi_response(environ,start_response)
    path = os.getcwd().replace('functions/', '')
    obj = db[path_components]
    config = f.WebConfig()
    prev = ' '.join(obj.prev.split()[:7])
    next = ' '.join(obj.next.split()[:7])
    current = obj.philo_id[:7]
    citation_hrefs = f.citation_links(db, config, obj)
    metadata_fields = {}
    for metadata in db.locals['metadata_fields']:
        metadata_fields[metadata] = obj[metadata]
    citation = biblio_citation(citation_hrefs, metadata_fields)
    if obj.philo_type == 'doc':
        resource = f.webResources("t_o_c", debug=db.locals["debug"])
        toc_object = generate_toc_object(obj, db)
        return render_template(obj=obj,philo_id=obj.philo_id[0],dbname=dbname,toc=toc_object, citation=citation,
                               db=db, q=q,config=config,template_name='t_o_c.mako', report="t_o_c", css=resource.css, js=resource.js)
    obj_text = f.get_text_obj(obj, path, query_args=q['byte'])
    resource = f.webResources("navigation", debug=db.locals["debug"])
    return render_template(obj=obj,philo_id=obj.philo_id[0],dbname=dbname,f=f,db=db,q=q,obj_text=obj_text,prev=prev,next=next,config=config,
                           citation=citation, template_name='object.mako', report="navigation", css=resource.css, js=resource.js)

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

def generate_toc_object(obj, db):
    """This function fetches all philo_ids for div elements within a doc"""
    config = f.WebConfig()
    conn = db.dbh 
    c = conn.cursor()
    doc_id =  int(obj.philo_id[0])
    next_doc_id = doc_id + 1
    c.execute('select rowid from toms where philo_id="%d 0 0 0 0 0 0"' % doc_id)
    start_rowid = c.fetchone()[0]
    c.execute('select rowid from toms where philo_id="%d 0 0 0 0 0 0"' % next_doc_id)
    try:
        end_rowid = c.fetchone()[0]
    except TypeError:
        c.execute('select rowid from toms where rowid > %d' % start_rowid)
        end_rowid = [i[0] for i in c.fetchall()][-1] + 1 ## we add 1 to make sure the last row of the table is included
    try:
        c.execute("select * from toms where rowid between ? and ? and philo_type>='div' and philo_type<='div3'", (start_rowid, end_rowid))
    except sqlite3.OperationalError:
        c.execute("select * from toms where rowid between ? and ? and  philo_type>='div' and philo_type<='div3'", (start_rowid, end_rowid))
    text_hierarchy = []
    for i in c.fetchall():
        if i['philo_name'] == '__philo_virtual' and i["philo_type"] != "div1":
            continue
        else:
            philo_id = i['philo_id']
            philo_type = i['philo_type']
            if i['philo_name'] == "front":
                display_name = "Front Matter"
            else:
                display_name = i['head']
                if display_name:
                    display_name = display_name.strip()
                if not display_name:
                    try:
                        display_name = i['type']
                    except:
                        pass
                    if not display_name:
                        display_name = i['philo_name'] or i['philo_type']
            display_name = display_name.decode('utf-8', 'ignore')
            display_name = display_name[0].upper() + display_name[1:]
            link = f.link.make_absolute_object_link(config, philo_id.split()[:7])
            toc_element = {"philo_id": philo_id, "philo_type": philo_type, "display_name": display_name, "link": link}
            text_hierarchy.append(toc_element)
    metadata_fields = {}
    for metadata in db.locals['metadata_fields']:
        if db.locals['metadata_types'][metadata] == "doc":
            metadata_fields[metadata] = obj[metadata]
    toc_object = {"toc": text_hierarchy, "metadata_fields": metadata_fields}
    return toc_object