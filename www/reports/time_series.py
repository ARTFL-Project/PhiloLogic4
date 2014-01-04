#!/usr/bin env python
from __future__ import division
import sys
sys.path.append('..')
import functions as f
from functions.wsgi_handler import wsgi_response
from bibliography import fetch_bibliography as bibliography
from render_template import render_template
from collections import defaultdict
import json

def time_series(environ,start_response):
    db, dbname, path_components, q = wsgi_response(environ,start_response)
    if q['q'] == '':
        return bibliography(f,path, db, dbname,q,environ)
    else:
        frequencies, relative_frequencies = generate_frequency(q, db)
        return render_template(frequencies=frequencies,relative_frequencies=relative_frequencies,
                               db=db,dbname=dbname,q=q,f=f, template_name='time_series.mako',
                               report="time_series")

def generate_frequency(q, db):
    """reads through a hitlist."""
    if q['start_date']:
        q['metadata']['date'] = '%s-' % q['start_date']
    if q['end_date']:
        if 'date' in q['metadata']:
            q['metadata']['date']+= '%s' % q['end_date']
        else:
            q['metadata']['date'] = '-%s' % q['end_date']
    
    results = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
    try:
        start = int(q['start_date'])
    except ValueError:
        start = float("-inf")
    try:
        end = int(q['end_date'])
    except ValueError:
        end = float("inf")
    
    counts = defaultdict(int)
    for i in results:
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
        
        counts[date] += 1
    
    absolute_count = [('Date', 'Count')]
    relative_count = {}
    for k,v in sorted(counts.iteritems(),key=lambda x: x[0], reverse=False):
        absolute_count.append((str(k),v))
        relative_count[str(k)] = relative_frequency(k, v, db, q['year_interval'])
    
    relative_count = sorted(relative_count.items(), key=lambda x: x[0], reverse=False)
    relative_count.insert(0, ('Date', 'Count'))
    
    return (json.dumps(absolute_count), json.dumps(relative_count))
    
def relative_frequency(date, count, db, interval):
    dates = [date]
    if interval == '1':
        query = '''select sum(word_count) from toms where date="%d"''' % date
    else:
        if interval == '10':
            dates.append(date + 9)
        else:
            dates.append(date + 99)
        query = "select sum(word_count) from toms where date between '%d' and '%d'" % (tuple(dates))
        
    c = db.dbh.cursor()
    c.execute(query)
    return count / c.fetchone()[0] * 1000000

    
    