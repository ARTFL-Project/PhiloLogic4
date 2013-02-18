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
        return render_template(obj=obj,dbname=dbname,f=f,navigate_doc=navigate_doc,db=db,q=q,form=False,template_name='navigation.mako')
    else:
        return render_template(obj=obj,dbname=dbname,f=f,navigate_obj=navigate_obj,db=db,q=q,form=False,template_name='object.mako')

def navigate_doc(obj, db):
    print >> sys.stderr, type(obj.philo_id)
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
#        id = re.sub(' 0$', '', id)
#        hit_object = object_wrapper(id.split(), byte, db, obj_type=philo_type)
#        obj_name = getattr(hit_object, philo_type)
#        text_hierarchy.append(hit_object)
    return text_hierarchy

def navigate_obj(obj, query_args=False):
    path = "./data/TEXT/" + obj.filename
    file = open(path)
    byte_start = obj.byte_start
    file.seek(byte_start)
    width = obj.byte_end - byte_start
    raw_text = file.read(width)
    if query_args:
        bytes = sorted([int(byte) - byte_start for byte in query_args.split('+')])
        text_start, text_middle, text_end = f.format.chunkifier(raw_text, bytes, highlight=True)
        raw_text = text_start + text_middle + text_end
        ## temp hack until we work out how to format without loosing highlight
        ## tags
        raw_text = re.sub('<(/?span[^>]*)>', '[\\1]', raw_text)
        text_obj = f.format.formatter(raw_text).decode("utf-8","ignore")
        return text_obj.replace('[', '<').replace(']', '>')
    else:
        return f.format.formatter(raw_text).decode("utf-8","ignore")
