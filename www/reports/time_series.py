#!/usr/bin/env python

from __future__ import division
import os
import sys
sys.path.append('..')
import functions as f
import reports as r
from functions.wsgi_handler import WSGIHandler
from wsgiref.handlers import CGIHandler
from philologic.DB import DB
from collections import defaultdict
from copy import deepcopy
from operator import itemgetter
try:
    import simplejson as json
except ImportError:
    print >> sys.stderr, "Please install simplejson for better performance"
    import json
import re

sub_date = re.compile('date=[^&]*')

def time_series(environ,start_response):
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    request = handle_dates(request, db)
    hits = db.query(request["q"],request["method"],request["arg"],**request.metadata)
    time_series_object = generate_time_series(config, request, db, hits)
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response('200 OK',headers)
    yield json.dumps(time_series_object)
        
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
        setattr(q, 'start_date', min(dates))
    q.metadata['date'] = '%d' % q.start_date
    if not q['end_date']:
        setattr(q, 'end_date', max(dates))
    q.metadata['date'] += '-%d' % q.end_date
    return q

def generate_time_series(config, q, db, hits):    
    """reads through a hitlist to generate a time_series_object"""
    time_series_object = {'query': dict([i for i in q]), 'query_done': False}
    time_series_object['query']['date'] = q.metadata['date']
    if q.start_date:
        start = q.start_date
    else:
        start = float("-inf")
    if q.end_date:
        end = q.end_date
    else:
        end = float("inf")
    time_series_object['query']['start_date'] = start
    time_series_object['query']['end_date'] = end
    
    absolute_count = defaultdict(int)
    date_counts = {}
    
    ## Override default value of q.end for first batch of results
    if q.end == 0:
        q.end = 3000
    
    count = 0
    more_results = True
    try:
        for i in hits[q.start:q.end]:
            date = i.date
            try:
                if date:
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
                    print >> sys.stderr, "No valid dates for %s: %s, %s" % (i.filename, i.author, i.title)
                    continue
            except ValueError: ## No valid date
                continue
            
            count += 1
            if date not in absolute_count:
                end_date = date + int(q["year_interval"]) - 1
                date_range = "%d-%d" % (date, end_date)
                url = f.link.make_absolute_query_link(config, q, report="concordance", date=date_range, start="0", end="0")
                absolute_count[date] = {"label": date, "count": 0, "url": url}
            absolute_count[date]['count'] += 1
            
            if date not in date_counts:
                date_counts[date] = date_total_count(date, db, q['year_interval'])
    except IndexError:
        more_results = False
    
    time_series_object['more_results'] = more_results
    time_series_object['results_length'] = len(hits)
    time_series_object['query_done'] = hits.done
    time_series_object['results'] = {'absolute_count': absolute_count, 'date_count': date_counts}
    return time_series_object


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
    
if __name__ == '__main__':
    CGIHandler().run(time_series)