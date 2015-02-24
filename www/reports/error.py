#!/usr/bin/env python

import os
import traceback
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
    error_message = "Your query made PhiloLogic4 crash with the following traceback: <p style='margin-top:10px;'>%s</p>" % traceback.format_exc().replace('\n', '<br>')
    error_message += '<br>Check Apache log for more info'
    if report == "concordance" or report == "bibliography" or report == "concordance_from_collocation" or report == "error":
        concordance_object = {"error": error_message,
                              "description": {"start": 0, "end": 0, "results_per_page": q.results_per_page},
                              "query": dict([i for i in q]),
                              "results": [],
                              "results_length": 0,
                              "query_done": True,
                              }
        return ""#r.render_concordance(concordance_object, hits, config, q)
    elif report == "kwic":
        kwic_object = {"error": error_message,
                       "description": {"start": 0, "end": 0, "results_per_page": q.results_per_page},
                       "query": dict([i for i in q]),
                       "results": [],
                       "results_length": 0,
                       "query_done": True,
                       }
        return ""#r.render_kwic(kwic_object, hits, config, q)
    elif report == "collocation":
        collocation_object = {"error": error_message,
                              "query": dict([i for i in q]),
                              "results_length": 0,
                              "filter_list": [],
                              "all_collocates": {},
                              "left_collocates": {},
                              "right_collocates": {},
                              }
        return ""#r.render_collocation(collocation_object, q, config)
    elif report == "time_series":
        try:
            q = r.handle_dates(q, db)
        except ValueError:
            setattr(q, 'start_date', 0)
            setattr(q, 'end_date', 0)
            error_message += "<br>Your error is most likely due to the absence of a valid date in your database."
        time_series_object = {"error": error_message,
                              "query": dict([i for i in q]),
                              "results_length": 0,
                              "query_done": True,
                              "results": {"absolute_count": {}, "date_count": {}}
                             }
        return ""#r.render_time_series(time_series_object, q, config)