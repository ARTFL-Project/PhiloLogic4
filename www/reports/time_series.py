#!/usr/bin/env python

from __future__ import division
import sys
sys.path.append('..')
import functions as f
from functions.wsgi_handler import WSGIHandler
from wsgiref.handlers import CGIHandler
from philologic.DB import DB
from collections import defaultdict
import timeit
try:
    import simplejson as json
except ImportError:
    print >> sys.stderr, "Please install simplejson for better performance"
    import json


def time_series(environ,start_response):
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    time_series_object = generate_time_series(config, request, db)
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response('200 OK',headers)
    yield json.dumps(time_series_object)

def generate_time_series(config, q, db):
    time_series_object = {'query': dict([i for i in q]), 'query_done': False}
    start_date, end_date = get_start_end_date(db, start_date=q.start_date, end_date=q.end_date)    
    date_ranges = generate_date_ranges(start_date, end_date, q.year_interval)
    
    absolute_count = defaultdict(int)
    date_counts = {}
    total_hits = 0
    last_date_done = start_date
    start_time = timeit.default_timer()
    max_time = q.max_time or 10
    for start_range, date_range in date_ranges:
        q.metadata['date'] = date_range
        hits = db.query(q["q"],q["method"],q["arg"],**q.metadata)
        hits.finish()
        url = f.link.make_absolute_query_link(config, q, report="concordance", date=date_range, start="0", end="0")
        absolute_count[start_range] = {"label": start_range, "count": len(hits), "url": url}
        date_counts[start_range] = date_total_count(start_range, db, q['year_interval'])
        total_hits += len(hits)
        elapsed = timeit.default_timer() - start_time
        if elapsed > int(max_time): # avoid timeouts by splitting the query if more than q.max_time (in seconds) has been spent in the loop
            last_date_done = start_range
            break
        last_date_done = start_range
    
    time_series_object['results_length'] = total_hits
    if (last_date_done + int(q.year_interval)) >= end_date:
        time_series_object['more_results'] = False
    else:
        time_series_object['more_results'] =  True
        time_series_object['new_start_date'] = last_date_done + int(q.year_interval)
    time_series_object['results'] = {'absolute_count': absolute_count, 'date_count': date_counts}
        
    return time_series_object

def get_start_end_date(db, start_date=None, end_date=None):
    c = db.dbh.cursor()
    c.execute('select date from toms where philo_type="doc"')
    dates = []
    for i in c.fetchall():
        try:
            dates.append(int(i[0]))
        except ValueError:
            pass
    min_date = min(dates)
    start_date = start_date or min_date
    if start_date < min_date:
        start_date = min_date
    max_date = max(dates)
    end_date = end_date or max_date
    if end_date > max_date:
        end_date = max_date
    return start_date, end_date
    
def generate_date_ranges(start_date, end_date, interval):
    interval = int(interval)
    date_ranges = []
    for i in xrange(start_date, end_date, interval):
        start = i
        end = i + interval - 1
        if end > end_date:
            end = end_date
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