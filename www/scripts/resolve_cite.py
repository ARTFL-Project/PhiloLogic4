#!/usr/bin/env python

import os
import sys
import urlparse
import cgi
import re
import json
import sqlite3
sys.path.append('..')
import functions as f
import reports as r
from reports.table_of_contents import nav_query
from functions.ObjectFormatter import adjust_bytes
#from functions.wsgi_handler import WSGIHandler
from philologic.DB import DB
from philologic.HitWrapper import ObjectWrapper
from functions.wsgi_handler import WSGIHandler
from wsgiref.handlers import CGIHandler

def resolve_cite_service(environ,start_response):
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    c = db.dbh.cursor()
    q = request.q

    best_url = config['db_url']

    if " - " in q:
        milestone = q.split(" - ")[0]
    else:
        milestone = q

    milestone_segments = []
    last_segment = 0
    milestone_prefixes = []
    for separator in re.finditer(r' (?!\.)|\.(?! )',milestone):
        milestone_prefixes += [milestone[:separator.start()]]
        milestone_segments += [milestone[last_segment:separator.start()]]
        last_segment = separator.end()
    milestone_segments += [milestone[last_segment:]]
    milestone_prefixes += [milestone]

    print >> sys.stderr, "SEGMENTS",repr(milestone_segments)
    print >> sys.stderr, "PREFIXES",repr(milestone_prefixes)

    abbrev_match = None
    for pos,v in enumerate(milestone_prefixes):
        print >> sys.stderr, "QUERYING for abbrev = ", v
        abbrev_q = c.execute("SELECT * FROM toms WHERE abbrev = ?;",(v,)).fetchone()
        if abbrev_q:
            abbrev_match = abbrev_q

    print >> sys.stderr, "ABBREV", abbrev_match["abbrev"], abbrev_match["philo_id"]
    doc_obj = ObjectWrapper(abbrev_match['philo_id'].split(), db)

#    types = iter("div1","div2","div3")
#    current_type = types.next()

    nav = nav_query(doc_obj,db)

    best_match = None
    for n in nav:
        if n["head"] == request.q:
            print >> sys.stderr, "MATCH", n["philo_id"],n["n"],n["head"]
            best_match = n
            break
#    print >> sys.stderr, repr(toc)

    if best_match:
        type_offsets = {"doc": 1, "div1": 2, "div2": 3, "div3": 4, "para": 5}
        t = best_match['philo_type']
        short_id = best_match["philo_id"].split()[:type_offsets[t]]
        best_url = f.make_absolute_object_link(config,short_id)
        print >> sys.stderr, "BEST_URL", best_url

    status = '302 Found'
    redirect = config['db_url']
    headers = [('Location',best_url)]
    start_response(status,headers)

    return ""

if __name__ == "__main__":
    CGIHandler().run(resolve_cite_service)

