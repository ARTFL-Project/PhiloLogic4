#!/usr/bin/env python

import os
import sys
sys.path.append('..')
from functions.wsgi_handler import parse_cgi
from reports import get_neighboring_pages, render_template
from mako.template import Template
from philologic.HitWrapper import ObjectWrapper
import functions as f
import json

    
if __name__ == "__main__":
    environ = os.environ
    environ["SCRIPT_FILENAME"] = environ["SCRIPT_FILENAME"].replace('scripts/go_to_obj.py', '')
    path = os.getcwd().replace('scripts', '')
    db, path_components, q = parse_cgi(environ)
    philo_obj = ObjectWrapper(q['philo_id'].split(), db)
    print >> sys.stderr, "BYTE", philo_obj.byte_start
    prev_obj = ' '.join(philo_obj.prev.split()[:7])
    next_obj = ' '.join(philo_obj.next.split()[:7])
    text = f.get_text_obj(philo_obj, path)
    print "Content-Type: text/html\n"
    print json.dumps({'text': text, "prev": prev_obj, "next": next_obj})