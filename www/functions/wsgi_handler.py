#!/usr/bin/env python

import urllib
from wsgiref.util import shift_path_info
import urlparse
import re
import sys
import os
from philologic.DB import DB
from query_parser import query_parser

class WSGIHandler(object):
    def __init__(self,db,environ):
        self.path_info = environ.get("PATH_INFO", '')
        self.query_string = environ["QUERY_STRING"]
        self.script_filename = environ["SCRIPT_FILENAME"]
        self.cgi = urlparse.parse_qs(self.query_string,keep_blank_values=True)
        self.defaults = {
          "results_per_page":"25",
          "start":"0",
          "end":"25",
          "arg":"0",          
          "interval_start":"0",
          "interval_end":"3000",
        }
        self.metadata_fields = db.locals["metadata_fields"]
        self.metadata = {}
        num_empty = 0
        
        self.start = int(self['start'])
        self.end = int(self['end'])
        self.results_per_page = int(self['results_per_page'])
        self.interval_start = int(self['interval_start'])
        self.interval_end = int(self['interval_end'])
        
        # cgi parameter string hacks here.
        if 'q' in self.cgi:
            self.cgi['q'][0] = self.cgi["q"][0].replace("'", " ") ## HACK ALERT: this is for French.
            self.cgi['q'][0] = self.cgi["q"][0].replace(';', '')
            self.cgi['q'][0] = self.cgi["q"][0].replace(',', '')
            self.cgi['q'][0] = self.cgi["q"][0].replace('!', '')
            self.cgi['q'][0] = self.cgi["q"][0].replace('?', '')                        
        
        for field in self.metadata_fields:
            if field in self.cgi and self.cgi[field]:
                ## Hack to remove hyphens in Frantext
                if field != "date" and isinstance(self.cgi[field][0], str or unicode):
                    if not self.cgi[field][0].startswith('"'):
                        self.cgi[field][0] = self.cgi[field][0].replace('-', ' ')
                ## these ifs are to fix the no results you get when you do a metadata query
                if self["q"] != '':
                    self.metadata[field] = self.cgi[field][0]                    
                elif self.cgi[field][0] != '':
                    self.metadata[field] = self.cgi[field][0]
            if field not in self.cgi or not self.cgi[field][0]: ## in case of an empty query
                num_empty += 1
                
        self.metadata['philo_type'] = self['philo_type']
        
        if "q" in self.cgi:
            if self.cgi["q"][0] == "":
                self.no_q = True
            else:
                self.no_q = False
        
        if num_empty == len(self.metadata_fields):
            self.no_metadata = True
        else:
            self.no_metadata = False
        
        try:
            self.path_components = [c for c in self.path_info.split("/") if c]
            if self.path_components[0] == 'form':
                query['report'] = 'form'
        except:
            self.path_components = []

    def __getattr__(self,key):
        return self[key]

    def __getitem__(self,key):
        if key in self.cgi:
            return self.cgi[key][0]
        elif key in self.defaults:
            return self.defaults[key]
        else:
            return ""

    def __iter__(self):
        for key in self.cgi.keys():
            yield (key,self[key])

def wsgi_response(environ,start_response):
    status = '200 OK'
    cgi = urlparse.parse_qs(environ["QUERY_STRING"],keep_blank_values=True)
    if "format" in cgi and cgi['format'][0] == "json":
        headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    else:
        headers = [('Content-type', 'text/html; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)

def parse_cgi(environ):
    """ Parses CGI parameters from Apache, returns a tuple with a philologic database, remaining path components, and a query dict. """
    myname = environ["SCRIPT_FILENAME"]
    dbfile = os.path.dirname(myname) + "/data"
    db = DB(dbfile,encoding='utf-8')
    print >> sys.stderr, environ["QUERY_STRING"]
    cgi = urlparse.parse_qs(environ["QUERY_STRING"],keep_blank_values=True)
   
    query = {}
    query["report"] = cgi.get("report",[""])[0]
    query["q_string"] = environ["QUERY_STRING"] ## this might be useful to have around
    query["q"] = cgi.get("q",[""])[0]
    if isinstance(query["q"], str):
        query['q'] = query["q"].replace("'", " ") ## HACK ALERT: this is for French.
        query['q'] = query['q'].replace(';', '')
        query['q'] = query['q'].replace(',', '')
        query['q'] = query['q'].replace('!', '')
        query['q'] = query['q'].replace('?', '')
        #query['q'] = re.sub('\.([^*]*)', ' \\1', query['q'])
    query["method"] = cgi.get("method",[""])[0]

#    query['arg'] = cgi.get("arg", [None])[0]
#    if query["method"] == "proxy":
#        if query['arg'] is None:
#            query["arg"] = cgi.get("arg_proxy",[0])[0]
#    elif query["method"] == "phrase":
#        if query['arg'] is None:
#            query["arg"] = cgi.get("arg_phrase",[0])[0]
#    elif query["method"] == "sentence" or query["method"] == "cooc":
#        query["arg"] = "6"
#    if query['arg'] is None:
#        query['arg'] = 0

    query["arg"] = cgi.get("arg",[""])[0]
    query["format"] = cgi.get("format",[""])[0]
    query["results_per_page"] = int(cgi.get("pagenum",[25])[0])
    
    ## Hack so that even if there are multiple byte offsets
    ## we still have it stored as a string in query
    query["byte"] = '+'.join(cgi.get("byte",['']))
    
    ## This defines within how many words for collocation tables
    query["word_num"] = cgi.get("word_num",[5])[0]
    if query["word_num"]:
        query["word_num"] = int(query["word_num"])
    
    # This defines the collocate for collocation to concordance searches
    query["collocate"] = cgi.get("collocate",[""])[0]
    query['direction'] = cgi.get("direction",[""])[0]
    query['collocate_num'] = cgi.get("collocate_num", [""])[0]
    
    # This is for dynamically updating results in collocations and the sidebar
    query['interval_start'] = int(cgi.get('interval_start', [0])[0])
    query['interval_end'] = int(cgi.get('interval_end', [3000])[0])
    
    ## This is for frequency searches: raw count or per n number of words
    query["rate"] = cgi.get("rate", [""])[0]
    
    query['philo_type'] = cgi.get("philo_type", [''])[0]
    
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
    query["field"] = cgi.get("field",[""])[0]
    query["metadata"] = {}
    metadata_fields = db.locals["metadata_fields"]
    num_empty = 0
    for field in metadata_fields:
        if field in cgi and cgi[field]:
            ## Hack to remove hyphens in Frantext
            if field != "date" and isinstance(cgi[field][0], str or unicode):
                if not cgi[field][0].startswith('"'):
                    cgi[field][0] = cgi[field][0].replace('-', ' ')
            ## these ifs are to fix the no results you get when you do a metadata query
            if query["q"] != '':
                query["metadata"][field] = cgi[field][0]                    
            elif cgi[field][0] != '':
                query["metadata"][field] = cgi[field][0]
        if field not in cgi or not cgi[field][0]: ## in case of an empty query
            num_empty += 1
            
    query["metadata"]['philo_type'] = query['philo_type']
    
    if num_empty == len(metadata_fields):
        query["no_q"] = True
    else:
        query["no_q"] = False
    
    try:
        path_components = [c for c in environ["PATH_INFO"].split("/") if c]
        if path_components[0] == 'form':
            query['report'] = 'form'
    except:
        path_components = False
    
    return (db, path_components, query)
