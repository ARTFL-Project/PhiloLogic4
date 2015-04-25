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
    # hits = db.query(request["q"],request["method"],request["arg"],**request.metadata)
    time_series_object = generate_time_series(config, request, db)
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

def generate_time_series(config, q, db):
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
    total_hits = 0
    
    date_ranges = generate_date_ranges(q)
    for start_date, date_range in date_ranges:
        q.metadata['date'] = date_range
        hits = db.query(q["q"],q["method"],q["arg"],**q.metadata)
        ### Make sure hitlist is done:
        while not hits.done:
            hits.update()
        url = f.link.make_absolute_query_link(config, q, report="concordance", date=date_range, start="0", end="0")
        absolute_count[start_date] = {"label": start_date, "count": len(hits), "url": url}
        date_counts[start_date] = date_total_count(start_date, db, q['year_interval'])
        total_hits += len(hits)
    
    time_series_object['results_length'] = total_hits
    time_series_object['more_results'] = False
    time_series_object['query_done'] = True
    time_series_object['results'] = {'absolute_count': absolute_count, 'date_count': date_counts}
    
    print >> sys.stderr, repr(date_counts)
    
    return time_series_object

def generate_date_ranges(q):
    interval = int(q.year_interval)
    date_ranges = []
    for i in xrange(q.start_date, q.end_date, interval):
        start = i
        end = i + interval - 1
        date_range = "%d-%d" % (start, end)
        date_ranges.append((start,date_range))
    return date_ranges

def date_total_count(date, db, interval):
    if interval != '1':
        dates = [date]
        dates.append(date + (int(interval) - 1))
        query = 'select sum(word_count) from toms where date between "%d" and "%d"' % tuple(dates)
    else:
        query = "select sum(word_count) from toms where date='%s'" % date
    c = db.dbh.cursor()
    c.execute(query)
    count = c.fetchone()[0] or 0
    return count
    
if __name__ == '__main__':
    CGIHandler().run(time_series)