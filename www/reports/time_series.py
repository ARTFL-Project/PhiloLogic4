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
        
        results = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
        while True:
            if results.done:
                break
        frequencies, relative_frequencies = generate_time_series(q, db, results)
        return render_template(frequencies=frequencies,relative_frequencies=relative_frequencies,
                               db=db,dbname=dbname,q=q,f=f, template_name='time_series.mako',
                               total=len(results),report="time_series")

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
    
    absolute_count = {}
    for i in results[q['interval_start']:q['interval_end']]:
        date = i['date']
        try:
            if date != None:
                date = int(date)
                if not start <= date <= end :
                    continue
                if q["year_interval"] == "10":
                    date = int(str(date)[:3] + '0')
                elif q['year_interval'] == "100":
                    date = int(str(date)[:2] + '00')
            else:
                continue
        except ValueError: ## No valid date
            continue
        
        if date not in absolute_count:
            absolute_count[date] = {}
            absolute_count[date]['count'] = 0
            absolute_count[date]['url'] = make_link(date, q['q_string'], q['year_interval'], db.locals['db_url'])
        absolute_count[date]['count'] += 1
    
    relative_count = deepcopy(absolute_count)
    for date in relative_count:
        relative_count[date]['count'] = relative_frequency(date, absolute_count[date]['count'], db, q['year_interval'])
    
    return (json.dumps(absolute_count), json.dumps(relative_count))

def make_link(date, q_string, interval, db_url):
    if interval == '10':
        date = int(str(date)[:3] + '0')
        next = date + 9
        date = str(date) + '-' + str(next)
    else:
        date = int(str(date)[:2] + '00')
        next = date + 99
        date = str(date) + '-' + str(next)
    href = sub_date.sub('date=%s' % date, q_string)
    href = href.replace('time_series', 'concordance')
    href = db_url + '/dispatcher.py/?' + href
    return href


def relative_frequency(date, count, db, interval):
    dates = [date]
    if interval == '10':
        dates.append(date + 9)
    else:
        dates.append(date + 99)
    query = '''select count(*) from words where doc_ancestor in (select philo_id from toms where date between "%d" and "%d")''' % (tuple(dates))
        
    c = db.dbh.cursor()
    c.execute(query)
    return count / c.fetchone()[0] * 1000000

    
    
