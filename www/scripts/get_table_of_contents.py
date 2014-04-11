#!/usr/bin/env python

import os
import sys
sys.path.append('..')
from functions.wsgi_handler import parse_cgi
from wsgiref.handlers import CGIHandler
from philologic.HitWrapper import ObjectWrapper
from mako.template import Template
import reports as r
import functions as f
import json

obj_level = {'doc': 1, 'div1': 2, 'div2': 3, 'div3': 4}

def get_table_of_contents(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    environ["SCRIPT_FILENAME"] = environ["SCRIPT_FILENAME"].replace('scripts/get_table_of_contents.py', '')
    db, path_components, q = parse_cgi(environ)
    path = db.locals['db_path']
    path = path[:path.rfind("/data")]
    obj = ObjectWrapper(q['philo_id'].split(), db)
    results = r.navigate_doc(obj, db)
    if q['format'] == "json":
        html = ''
        for i in results:
            id = i.philo_id[:7]
            link_id = '_'.join([str(j) for j in i.philo_id])
            href = f.link.make_absolute_object_link(db,id)
            head_or_type = i.head or "[%s]" % i.type
            html += "<span>"
            style = ""
            if i.type == "div2":
                space = '&nbsp&nbsp&nbsp'
            elif i.type == "div3":
                space = '&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp'
            else:
                space = ''
            html += space + '<a href="%s" id="%s" style="text-decoration: none;">%s</a></span><br>' % (href, link_id, head_or_type)
        yield json.dumps(html)
    else:
        html = '<div id="table_of_contents" class="table_of_contents">'
        for i in results:
            id = i.philo_id[:7]
            link_id = '_'.join([str(j) for j in i.philo_id])
            href = f.link.make_absolute_object_link(db,id)
            head_or_type = i.head or "[%s]" % i.type
            html += '<span class="toc_link">'
            style = ""
            if i.type == "div2":
                space = '<span class="ui-icon ui-icon-radio-on" style="float:left;position:relative;top:3px;margin-left: 1em;"></span>'
            elif i.type == "div3":
                space = '<span class="ui-icon ui-icon-radio-off" style="float:left;top:3px;position:relative;margin-left: 2em;"></span>'
            else:
                space = '<span class="ui-icon ui-icon-bullet" style="float:left;position:relative;top: 3px;"></span>'
            html += space + '<a href="%s" id="%s">%s</a></span>' % (href, link_id, head_or_type)
        html += "</div>"
        yield html.encode('utf-8', 'ignore')
    
if __name__ == "__main__":
    CGIHandler().run(get_table_of_contents)