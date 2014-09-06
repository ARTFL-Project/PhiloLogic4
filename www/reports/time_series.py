#!/usr/bin env python
from __future__ import division
import os
import sys
sys.path.append('..')
import functions as f
from functions.wsgi_handler import wsgi_response
from functions import concatenate_files
from bibliography import fetch_bibliography as bibliography
from render_template import render_template
from collections import defaultdict
from copy import deepcopy
from operator import itemgetter
import json
import re

sub_date = re.compile('date=[^&]*')

def time_series(environ,start_response):
    db, dbname, path_components, q = wsgi_response(environ,start_response)
    path = os.getcwd().replace('functions/', '')
    config = f.WebConfig()
    if q['q'] == '':
        return bibliography(f,path, db, dbname,q,environ)
    else:
        q = handle_dates(q, db)
        hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
        return render_time_series(hits, db, dbname, q, path, config)
        
def handle_dates(q, db):
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
    return q
    

def render_time_series(hits, db, dbname, q, path, config):
    concatenate_files(path, "time_series", debug=db.locals["debug"])
    biblio_criteria = f.biblio_criteria(q, config, time_series=True)
    frequencies, date_counts = generate_time_series(q, db, hits)
    return render_template(frequencies=frequencies,db=db,dbname=dbname,q=q,f=f, template_name='time_series.mako',
                           biblio_criteria=biblio_criteria, date_counts=date_counts,
                           config=config, total=len(hits),report="time_series", scripts=f.concatenate.report_files['js']["time_series"])

def generate_time_series(q, db, results):    
    """reads through a hitlist."""    
    try:
        start = int(q['start_date'])
    except ValueError:
        start = float("-inf")
    try:
        end = int(q['end_date'])
    except ValueError:
        end = float("inf")
    
    absolute_count = defaultdict(int)
    date_counts = {}
    print >> sys.stderr, "INTERVAL", q["year_interval"]
    for i in results[q['interval_start']:q['interval_end']]:
        date = i.doc['date']
        try:
            if date != None:
                date = int(date)
                if not date <= end :
                    continue
                if q["year_interval"] == "10":
                    date = int(str(date)[:-1] + '0')
                elif q['year_interval'] == "100":
                    date = int(str(date)[:-2] + '00')
                elif q['year_interval'] == '50':
                    decade = int(str(date)[-2:])
                    if decade < 50:
                        date = int(str(date)[:-2] + '00')
                    else:
                        date = int(str(date)[:-2] + '50')
                    
            else:
                continue
        except ValueError: ## No valid date
            continue
        
        absolute_count[date] += 1
        
        if date not in date_counts:
            date_counts[date] = date_total_count(date, db, q['year_interval'])
    
    print >> sys.stderr, absolute_count
    return json.dumps(absolute_count), json.dumps(date_counts)


def date_total_count(date, db, interval):
    
    if interval != '1':
        dates = [date]
        if interval == '10':
            dates.append(date + 9)
        elif interval == "50":
            dates.append(date + 49)
        else:
            dates.append(date + 99)
        query = 'select sum(word_count) from toms where date between "%d" and "%d"' % tuple(dates)
    else:
        query = "select sum(word_count) from toms where date='%s'" % date
    
    c = db.dbh.cursor()
    c.execute(query)
    return c.fetchone()[0]
    
    
    


    
    
