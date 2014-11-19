#!/usr/bin/env python

import os
import sys
sys.path.append('..')
from functions.wsgi_handler import WSGIHandler
from wsgiref.handlers import CGIHandler
from philologic.DB import DB
from philologic.HitWrapper import ObjectWrapper
from lxml import etree
import functions as f
import re

header_name = 'teiHeader'  ## Not sure if this should be configurable

def get_header(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    path = config.db_path
    obj = ObjectWrapper(request['philo_id'].split(), db)
    filename = path + '/data/TEXT/' + obj.filename
    parser = etree.XMLParser(remove_blank_text=True, recover=True)
    xml_tree = etree.parse(filename, parser)
    header = xml_tree.find(header_name)
    try:
        header_text = etree.tostring(header, pretty_print=True)
    except TypeError: ## workaround for when lxml doesn't find the header for whatever reason
        header_text = ''
        start = 0
        for line in open(filename):
            if re.search('<%s' % header_name, line):
                start = 1
            if start:
                header_text += line
            if re.search('</%s' % header_name, line):
                break        
    yield header_text.replace('<', '&lt;').replace('>', '&gt;')
    
if __name__ == "__main__":
    CGIHandler().run(get_header)