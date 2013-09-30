#!/usr/bin env python
from __future__ import division
import sys
sys.path.append('..')
import functions as f
from functions.wsgi_handler import wsgi_response
from render_template import render_template
from collections import defaultdict
import json

def time_series(environ,start_response):
    db, dbname, path_components, q = wsgi_response(environ,start_response)
    frequencies, relative_frequencies = generate_frequency(q, db)
    #frequencies, relative_frequencies = time_frequency(q, db)
    return render_template(frequencies=frequencies,relative_frequencies=relative_frequencies,
                           db=db,dbname=dbname,q=q,f=f, template_name='time_series.mako')

def time_frequency(q, db):
    try:
        start = int(q['start_date'])
    except ValueError:
        start = float("-inf")
    try:
        end = int(q['end_date'])
    except ValueError:
        end = float("inf")
    conn = db.dbh
    c = conn.cursor()
    query_words = q['q'].replace('|', ' ') ## Handle ORs from crapser
    q['q'] = q['q'].replace(' ', '|') ## Add ORs for search links
    if len(query_words.split()) > 1:
        query = 'select ranked_relevance.philo_id, ranked_relevance.token_count, toms.word_count, toms.date from ranked_relevance inner join toms on toms.philo_id=ranked_relevance.philo_id and toms.philo_name!="__philo_virtual" where '
        words =  query_words.split()
        query += ' or '.join(['ranked_relevance.philo_name=?' for i in words])
        c.execute(query, words)
    else:
        query = 'select ranked_relevance.philo_id, ranked_relevance.token_count, toms.word_count, toms.date from ranked_relevance inner join toms on toms.philo_id=ranked_relevance.philo_id and toms.philo_name!="__philo_virtual" where ranked_relevance.philo_name=?'
        c.execute(query, (query_words,))
    counts = {}
    relative_counts = {}
    for i in c.fetchall():
        count = int(i['token_count'])
        try:
            if i['date'] != None:
                date = int(i['date'])
                if q["year_interval"] == "1":
                    date = date
                elif q["year_interval"] == "10":
                    date = int(str(date)[:3] + '0')
                else:
                    date = int(str(date)[:2] + '00')
            else:
                continue
        except ValueError: ## No valid date
            continue
        if not start <= date <= end :
            continue
        if date not in counts:
            counts[date] = 0
            relative_counts[date] = 0
        counts[date] += count
        relative_counts[date] += int(i['word_count'])
        
    current_date = False
    interval = int(q['year_interval'])
    new_counts = {}
    new_relative_counts = {}
    for d, c in sorted(counts.iteritems(), key=lambda x: x[0]):
        if not current_date:
            current_date = d
            new_counts[str(d)] = c
            new_relative_counts[str(d)] = relative_counts[d] 
            continue
        current_date += interval
        if d != current_date:
            while current_date < d:
                print >> sys.stderr, current_date, d
                new_counts[str(current_date)] = 0
                new_relative_counts[str(current_date)] = 1
                current_date += interval
        new_counts[str(d)] = c
        new_relative_counts[str(d)] = relative_counts[d]
                
        
            
    relative_counts = dict([(date, new_counts[date] / new_relative_counts[date] * 10000) for date in new_counts])
        
    table = sorted(new_counts.iteritems(),key=lambda x: x[0], reverse=False)
    relative_table = sorted(relative_counts.iteritems(),key=lambda x: x[0], reverse=False)
    
    table.insert(0, ('Date', 'Count'))
    relative_table.insert(0, ('Date', 'Count'))
    return (json.dumps(table), json.dumps(relative_table))

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

    
    