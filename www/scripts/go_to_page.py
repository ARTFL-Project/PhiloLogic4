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
    doc_id = q['philo_id'].split()[0]
    philo_id = doc_id + " %"
    c = db.dbh.cursor()
    c.execute('select filename from toms where philo_id like ? and philo_type="doc"', (philo_id,))
    filename = c.fetchone()[0]
    if q['go_to_page'] == 'prev_page':
        doc_page = str(int(q['doc_page']) - 1)
    else:
        doc_page = str(int(q['doc_page']) + 1)
    page_text = f.get_page_text(db, doc_id, doc_page, filename, path, q['byte'])
    prev_page, next_page = get_neighboring_pages(db, doc_id, q['doc_page'])
    print "Content-Type: text/html\n"
    print page_text.encode('utf-8', 'ignore')