#!/usr/bin/env python

import os
import sys
sys.path.append('..')
import functions as f
import reports as r
import json
from philologic.HitList import NoHits
from philologic.DB import DB
from functions.wsgi_handler import WSGIHandler


def error(environ,start_response):
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    headers = [('Content-type', 'text/html; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    try:
        start_response('200 OK',headers)
    except AssertionError: ## headers already set
        pass
    return error_handling(db, config, request)
    
def error_handling(db, config, q):
    hits = NoHits()
    path = config.db_path
    report = q['report']
    hits = NoHits()
    if report == "concordance" or report == "bibligraphy":
        concordance_object = {"description": {"start": 0, "end": 0, "results_per_page": q.results_per_page},
                              "query": dict([i for i in q]),
                              "results": [],
                              "results_length": 0,
                              "query_done": True
                              }
        return r.render_concordance(concordance_object, hits, config, q)
    elif report == "kwic":
        kwic_object = {"description": {"start": 0, "end": 0, "results_per_page": q.results_per_page},
                       "query": dict([i for i in q]),
                       "results": [],
                       "results_length": 0,
                       "query_done": True
                       }
        return r.render_kwic(kwic_object, hits, config, q)
    elif report == "collocation":
        return r.render_collocation(hits, q, config)
    elif report == "time_series":
        q = r.handle_dates(q, db)
        return r.render_time_series(hits, db, q, config)