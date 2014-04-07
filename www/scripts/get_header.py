#!/usr/bin/env python

import os
import sys
sys.path.append('..')
from functions.wsgi_handler import parse_cgi
from wsgiref.handlers import CGIHandler
from philologic.HitWrapper import ObjectWrapper
from mako.template import Template
from lxml import etree
import reports as r
import functions as f
import json

obj_level = {'doc': 1, 'div1': 2, 'div2': 3, 'div3': 4}

def get_header(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    environ["SCRIPT_FILENAME"] = environ["SCRIPT_FILENAME"].replace('scripts/get_header.py', '')
    db, path_components, q = parse_cgi(environ)
    path = db.locals['db_path']
    path = path[:path.rfind("/data")]
    obj = ObjectWrapper(q['philo_id'].split(), db)
    filename = path + '/data/TEXT/' + obj.filename
    parser = etree.XMLParser(remove_blank_text=True)
    xml_tree = etree.parse(filename, parser)
    header = xml_tree.find('teiHeader')
    header_text = etree.tostring(header, pretty_print=True).replace('<', '&lt;').replace('>', '&gt;')
    yield header_text
    
if __name__ == "__main__":
    CGIHandler().run(get_header)