#!/usr/bin/env python

import urlparse
import sys
import Cookie
import hashlib
from philologic.DB import DB

class WSGIHandler(object):
    def __init__(self,db,environ):        
        self.path_info = environ.get("PATH_INFO", '')
        self.query_string = environ["QUERY_STRING"]
        self.script_filename = environ["SCRIPT_FILENAME"]
        self.cookies = Cookie.SimpleCookie(environ["HTTP_COOKIE"])

        try:
            h = hashlib.md5()
            secret = ""
            h.update(environ['REMOTE_ADDR'])
            h.update(self.cookies["timestamp"])
            h.update(secret)
            print >> sys.stderr, "COOKIE: ", self.cookies["hash"], " vs ", h.hexdigest()       
        except: 
            pass
        self.cgi = urlparse.parse_qs(self.query_string,keep_blank_values=True)
        self.defaults = {
          "results_per_page":"25",
          "start":"0",
          "end":"0",
          #"arg":"0",          
        }

        ## Check the header for JSON content_type or look for a format=json keyword
        if 'CONTENT_TYPE' in environ:
            self.content_type = environ['CONTENT_TYPE']
        else:
            self.content_type = 'text/HTML'
        ## If format is set, it overrides the content_type
        if "format" in self.cgi:
            if self.cgi['format'][0] == "json":
                self.content_type = "application/json"
            else:
                self.content_type = self.cgi['format'][0] or ''
        
        # Make byte a direct attribute of the class since it is a special case and
        # can contain more than one element
        if "byte" in self.cgi:
            self.byte = self.cgi['byte']

        ## Temporary fix for search term arguments before new core merge
        method = self["method"] or "proxy"
        arg = self["arg"]
        if method == "proxy":
            if not arg:
                arg = self["arg_proxy"]
        elif method == "phrase":
            if not arg:
                arg = self["arg_phrase"]
        elif method == "sentence" or method == "cooc":
            arg = "6"
        if not arg:
            arg = 0
        self.arg = arg
        self.cgi['arg'] = [arg]
        
        self.metadata_fields = db.locals["metadata_fields"]
        self.metadata = {}
        num_empty = 0
        
        self.start = int(self['start'])
        self.end = int(self['end'])
        self.results_per_page = int(self['results_per_page'])
        if self.start_date:
            self.start_date = int(self['start_date'])
        if self.end_date:
            self.end_date = int(self['end_date'])
        
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
