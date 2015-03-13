#!/usr/bin/env python

import sys
sys.path.append('..')
from wsgiref.handlers import CGIHandler
from philologic.DB import DB
import functions as f
import reports as r
import json

def get_start_end_date(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    c = db.dbh.cursor()
    c.execute('select date from toms where philo_type="doc"')
    dates = []
    for i in c.fetchall():
        try:
            dates.append(int(i[0]))
        except ValueError:
            pass
    yield json.dumps({"start_date": min(dates), "end_date": max(dates)})
    
if __name__ == "__main__":
    CGIHandler().run(get_start_end_date)