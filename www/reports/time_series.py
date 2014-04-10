#!/usr/bin env python
from __future__ import division
import os
import sys
sys.path.append('..')
import functions as f
from functions.wsgi_handler import wsgi_response
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
    if q['q'] == '':
        return bibliography(f,path, db, dbname,q,environ)
    else:
        if q['start_date']:
            q['metadata']['date'] = '%s-' % q['start_date']
        if q['end_date']:
            if 'date' in q['metadata']:
                q['metadata']['date']+= '%s' % q['end_date']
            else:
                q['metadata']['date'] = '-%s' % q['end_date']
        biblio_criteria = " ".join([k + "=" + v for k,v in q["metadata"].iteritems() if v])
        results = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
        frequencies, date_counts = generate_time_series(q, db, results)
        return render_template(frequencies=frequencies,db=db,dbname=dbname,q=q,f=f, template_name='time_series.mako',
                               biblio_criteria=biblio_criteria, date_counts=date_counts, total=len(results),report="time_series")

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
    if not q['interval_start']:
        q['interval_end'] = 10000  ## override defaults since this is faster than collocations
    for i in results[q['interval_start']:q['interval_end']]:
        date = i.doc['date']
        try:
            if date != None:
                date = int(date)
                if not start <= date <= end :
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
    
    return json.dumps(absolute_count), json.dumps(date_counts)


def date_total_count(date, db, interval):
    dates = [date]
    if interval == '10':
        dates.append(date + 9)
    else:
        dates.append(date + 99)
    #query = '''select count(*) from words where doc_ancestor in (select philo_id from toms where date between "%d" and "%d")''' % (tuple(dates))
    query = 'select sum(word_count) from toms where date between "%d" and "%d"' % tuple(dates)
    
    c = db.dbh.cursor()
    c.execute(query)
    return c.fetchone()[0]
    
    
    


    
    
