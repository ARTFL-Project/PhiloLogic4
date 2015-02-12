#!/usr/bin/env python

import os
import sys
sys.path.append('..')
from functions.wsgi_handler import WSGIHandler
from philologic.DB import DB
import functions as f


def landing_page(environ,start_response):
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    headers = [('Content-type', 'text/html; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response('200 OK',headers)
    return build_html_page(config)

def build_html_page(config):
    html_page = open('%s/templates/philoLogicHome.html' % config.db_path).read()
    html_page = html_page.replace('$DBNAME', config.dbname)
    html_page = html_page.replace('$DBURL', config.db_url)
    html_page = html_page.replace('$PHILOCONFIG', config.toJSON())
    return html_page