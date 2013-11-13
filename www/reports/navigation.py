#!/usr/bin/env python

import sys
sys.path.append('..')
import os
import sqlite3
import sys
import functions as f
from functions.wsgi_handler import wsgi_response
from render_template import render_template

philo_types = set(['div1', 'div2', 'div3'])

def navigation(environ,start_response):
    db, dbname, path_components, q = wsgi_response(environ,start_response)
    path = os.getcwd().replace('functions/', '')
    obj = db[path_components]
    if obj.philo_type == 'doc':
        return render_template(obj=obj,philo_id=obj.philo_id[0],dbname=dbname,f=f,navigate_doc=navigate_doc,
                       db=db,q=q,template_name='t_o_c.mako')
    else:
        obj_text = f.get_text_obj(obj, path, query_args=q['byte'])
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
