#!/usr/bin/env python

import urllib
from wsgiref.util import shift_path_info
import urlparse
import re
import sys
import os
from philologic.DB import DB
from philologic.Query import word_pattern_search
from query_parser import query_parser


def wsgi_response(environ,start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    environ["parsed_params"] = urlparse.parse_qs(environ["QUERY_STRING"],keep_blank_values=True)
    myname = environ["SCRIPT_FILENAME"]
    dbname = os.path.basename(myname.replace("/dispatcher.py",""))
    db, path_components, q = parse_cgi(environ)
    return db, dbname, path_components, q

def parse_cgi(environ):
    """ Parses CGI parameters from Apache, returns a tuple with a philologic database, remaining path components, and a query dict. """
    myname = environ["SCRIPT_FILENAME"]
    dbfile = os.path.dirname(myname) + "/data"
    db = DB(dbfile,encoding='utf-8')
    print >> sys.stderr, environ["QUERY_STRING"]
    cgi = urlparse.parse_qs(environ["QUERY_STRING"],keep_blank_values=True)
   
    query = {}
    query["q_string"] = environ["QUERY_STRING"] ## this might be useful to have around
    query["q"] = cgi.get("q",[None])[0]
    query["method"] = cgi.get("method",[None])[0]
    query['arg'] = cgi.get("arg", [None])[0]
    if query["method"] == "proxy":
        if query['arg'] is None:
            query["arg"] = cgi.get("arg_proxy",[0])[0]
    elif query["method"] == "phrase":
        if query['arg'] is None:
            query["arg"] = cgi.get("arg_phrase",[0])[0]
    elif query["method"] == "sentence" or query["method"] == "cooc":
        query["arg"] = "6"
    if query['arg'] is None:
        query['arg'] = 0
    query["report"] = cgi.get("report",[None])[0]
    query["format"] = cgi.get("format",[None])[0]
    query["results_per_page"] = int(cgi.get("pagenum",[50])[0])
    
    ## Hack so that even if there are multiple byte offsets
    ## we still have it stored as a string in query
    query["byte"] = '+'.join(cgi.get("byte",['']))
    
    ## This defines within how many words for collocation tables
    query["word_num"] = cgi.get("word_num",[5])[0]
    if query["word_num"]:
        query["word_num"] = int(query["word_num"])
    
    # This defines the collocate for collocation to concordance searches
    query["collocate"] = cgi.get("collocate",[None])[0]
    query['direction'] = cgi.get("direction",[None])[0]
    query['collocate_num'] = cgi.get("collocate_num", [None])[0]
    
    # This is for dynamically updating results in collocations and the sidebar
    query['interval_start'] = int(cgi.get('interval_start', [0])[0])
    query['interval_end'] = int(cgi.get('interval_end', [50])[0])
    
    ## This is for frequency searches: raw count or per n number of words
    query["rate"] = cgi.get("rate", [None])[0]
    
    ## This is for ranked relevancy
    query['obj_type'] = 'doc'
    
    ## This is for theme rheme searches
    query['theme_rheme'] = cgi.get("theme_rheme", [''])[0]
    
    ## This is for searches done from the bibliography template and possibly other use cases
    query['philo_id'] = cgi.get("philo_id", [''])[0]
    
    ## This is for time series
    query['start_date'] = cgi.get("start_date", [''])[0]
    query['end_date'] = cgi.get("end_date", [''])[0]
    query['year_interval'] = cgi.get("year_interval", [''])[0]
    
    ## This is for document page navigation
    query['doc_page'] = cgi.get('doc_page', [''])[0]
    query['philo_id'] = cgi.get('philo_id', [''])[0]
    query['filename'] = cgi.get('filename', [''])[0]
    query['go_to_page'] = cgi.get('go_to_page', [''])[0]
    
#    query["dbname"] = dbname
    query["dbpath"] = dbfile
    query["start"] = int(cgi.get('start',[0])[0]) # special range handling done in each service now.
    query["end"] = int(cgi.get('end',[0])[0]) 
    query["width"] = int(cgi.get("width",[0])[0]) or 300
    query["field"] = cgi.get("field",[None])[0]
    query["metadata"] = {}
    metadata_fields = db.locals["metadata_fields"]
    num_empty = 0
    for field in metadata_fields:
        if field in cgi and cgi[field]:
            ## these ifs are to fix the no results you get when you do a metadata query
            if query["q"] != '':
                query["metadata"][field] = cgi[field][0]
            elif cgi[field][0] != '':
                query["metadata"][field] = cgi[field][0]
        if field not in cgi or not cgi[field][0]: ## in case of an empty query
            num_empty += 1
    
    if num_empty == len(metadata_fields):
        query["no_q"] = True
    else:
        query["no_q"] = False
    
    #if query['q']:
    #    query['q'] = query_parser(query['q'])
    
    try:
        path_components = [c for c in environ["PATH_INFO"].split("/") if c]
        if path_components[0] == 'form':
            query['report'] = 'form'
    except:
        path_components = False
    
    return (db, path_components, query)
