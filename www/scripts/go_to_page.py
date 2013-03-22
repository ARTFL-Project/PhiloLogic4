#!/usr/bin/env python

import os
import sys
sys.path.append('..')
from functions.wsgi_handler import parse_cgi
from reports import get_neighboring_pages, render_template
from mako.template import Template
import functions as f
import json

    
if __name__ == "__main__":
    environ = os.environ
    environ["SCRIPT_FILENAME"] = environ["SCRIPT_FILENAME"].replace('scripts/go_to_page.py', '')
    path = os.getcwd().replace('scripts', '')
    db, path_components, q = parse_cgi(environ)
    doc_id = str(q['philo_id'].split()[0]) + ' %'
    philo_id = doc_id + " %"
    c = db.dbh.cursor()
    c.execute('select filename from toms where philo_type="doc" and philo_id like ?', (philo_id,))
    filename = c.fetchone()[0]
    page_text = f.get_page_text(db, doc_id, q['go_to_page'], filename, path, q['byte'])
    prev_page, next_page = get_neighboring_pages(db, doc_id, q['go_to_page'])
    print "Content-Type: text/html\n"
    print json.dumps([prev_page, next_page, q['go_to_page'], page_text.encode('utf-8', 'ignore')])