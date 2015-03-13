#! /usr/bin/env python

import os
import sys
try:
    import simplejson as json
except ImportError:
    print >> sys.stderr, "Please install simplejson for better performance"
    import json
from philologic.DB import DB
from search_utilities import search_examples

valid_time_series_intervals = set([1, 10, 50, 100])

class WebConfig(object):
    
    def __init__(self):
        self.config = {}
        self.db_path = os.path.abspath(os.path.dirname(__file__)).replace('functions', '')
        self.db_name = os.path.basename(self.db_path)
        db = DB(self.db_path + '/data',encoding='utf-8')
        web_config_path = self.db_path + "/data/web_config.cfg"
        try:
            execfile(web_config_path, globals(), self.config)
        except NameError:
            ##TODO: redirect to an error page indicating a syntax error
            raise SyntaxError
        
        self.config['debug'] = db.locals['debug']
        self.config['db_path'] = self.db_path
        self.config['db_name'] = self.db_name
        
        for i in self.config['metadata']:
            if i not in self.config['search_examples']:
                self.config['search_examples'][i] = search_examples(i)
            else:
                self.config['search_examples'][i] = self.config['search_examples'][i].decode('utf-8', 'ignore')
    
    def __getattr__(self, attr):
        return self.get_config(attr)
    
    def __getitem__(self, item):
        return self.get_config(item)
        
    def get_config(self, item):
        try:
            config_option = self.config[item]
            if not config_option and item == "time_series_intervals":
                config_option = [i for i in config_option if i in valid_time_series_intervals]
            elif not config_option and item == "landing_page_browsing":
                if "start" not in config_option["date"] or "end" not in config_option["date"] or "interval" not in config_option["date"]:
                    config_option["date"] = {}
            if item == "stopwords":
                config_option = os.path.join(self.db_path, "data", config_option)
                if not os.access(config_option, os.R_OK):
                    config_option = ''
        except KeyError:
            config_option = []
        return config_option
        
    def toJSON(self):
        config_obj = dict([(option, self[option]) for option in self.config])
        return json.dumps(config_obj)
