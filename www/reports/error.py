#!/usr/bin/env python

import os
import sys
sys.path.append('..')
import functions as f
import json
from functions.wsgi_handler import wsgi_response, parse_cgi
from concordance import fetch_concordance
from kwic import fetch_kwic
from collocation import fetch_collocation, sort_to_display
from time_series import generate_time_series
from render_template import render_template


class noHits(object):
    
    def __init__(self):
        self.done = True
    
    def __len__(self):
        return 0
    
    def __getitem__(self, item):
        return ''
    
    def __iter__(self):
        return ''

def error(environ,start_response):
    config = f.WebConfig()
    try:
        db, dbname, path_components, q = wsgi_response(environ,start_response)
    except AssertionError:
        myname = environ["SCRIPT_FILENAME"]
        dbname = os.path.basename(myname.replace("/dispatcher.py",""))
        db, path_components, q = parse_cgi(environ)
    report = q['report']
    path = os.getcwd().replace('functions/', '')
    biblio_criteria = f.biblio_criteria(q, config)
    hits = noHits()
    if report == "concordance":
        return render_template(results=hits,db=db,dbname=dbname,q=q,fetch_concordance=fetch_concordance,
                               f=f, path=path, results_per_page=q['results_per_page'],biblio_criteria=biblio_criteria,
                               config=config,template_name="concordance.mako", report="concordance")
    elif report == "kwic":
        return render_template(results=hits,db=db,dbname=dbname,q=q,fetch_kwic=fetch_kwic,f=f,
                                path=path, results_per_page=q['results_per_page'], biblio_criteria=biblio_criteria,
                                config=config, template_name='kwic.mako', report="kwic")
    elif report == "collocation":
        all_colloc, left_colloc, right_colloc = fetch_collocation(hits, path, q, db)
        hit_len = len(hits)
        return render_template(all_colloc=all_colloc, left_colloc=left_colloc, right_colloc=right_colloc,
                           db=db,dbname=dbname,q=q,f=f,path=path, results_per_page=q['results_per_page'],
                           hit_len=hit_len, order=sort_to_display,dumps=json.dumps,biblio_criteria=biblio_criteria,
                           config=config, template_name='collocation.mako', report="collocation")
    elif report == "time_series":
        frequencies, date_counts = generate_time_series(q, db, hits)
        c = db.dbh.cursor()
        c.execute('select date from toms where philo_type="doc"')
        dates = []
        for i in c.fetchall():
            try:
                dates.append(int(i[0]))
            except ValueError:
                pass
        if not q['start_date']:
            q['start_date'] = str(min(dates))
        q['metadata']['date'] = '%s' % q['start_date']
        if not q['end_date']:
            q['end_date'] = str(max(dates))
        q['metadata']['date'] += '-%s' % q['end_date']
        biblio_criteria = f.biblio_criteria(q, config, time_series=True)
        return render_template(frequencies=frequencies,db=db,dbname=dbname,q=q,f=f, template_name='time_series.mako',
                               biblio_criteria=biblio_criteria, date_counts=date_counts,
                               config=config, total=len(hits),report="time_series")
    
#def error(environ,start_response):
#    config = f.WebConfig()
#    try:
#        db, dbname, path_components, q = wsgi_response(environ,start_response)
#    except AssertionError:
#        myname = environ["SCRIPT_FILENAME"]
#        dbname = os.path.basename(myname.replace("/dispatcher.py",""))
#        db, path_components, q = parse_cgi(environ)
#    return render_template(db=db,dbname=dbname,form=True, q=q, config=config,
#                           report="error", template_name='error.mako')

