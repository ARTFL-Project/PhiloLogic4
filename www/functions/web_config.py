#! /usr/bin/env python

import os
import sys
from json import dumps
from search_utilities import search_examples

valid_time_series_intervals = set([1, 10, 50, 100])

class WebConfig(object):
    
    def __init__(self):
        self.config = {}
        path = os.path.abspath(os.path.dirname(__file__)).replace('functions', '') + "/data/web_config.cfg" 
        try:
            execfile(path, globals(), self.config)
        except SyntaxError:
            raise SyntaxError
        if self.config['search_examples'] == None:
            self.config['search_examples'] = {}
        for i in self.config['metadata']:
            if i not in self.config['search_examples']:
                self.config['search_examples'][i] = search_examples(i)
            else:
                self.config['search_examples'][i] = self.config['search_examples'][i].decode('utf-8', 'ignore')
                
        self.options = set(['db_url', 'dbname', 'concordance_length', 'facets', 'metadata',
                        'search_reports', 'metadata_aliases', 'search_examples', 'time_series_intervals', "theme"])
    
    def __getattr__(self, attr):
        if attr in self.options:
            return self.get_config(attr)
        else:
            print >> sys.stderr, "### Web Configuration Error ###"
            print >> sys.stderr, 'This variable is not supported in the current code base'
            raise AttributeError
    
    def __getitem__(self, item):
        if item in self.options:
            return self.get_config(item)
        else:
            print >> sys.stderr, "### Web Configuration Error ###"
            print >> sys.stderr, 'This variable is not supported in the current code base'
            raise KeyError
        
    def get_config(self, item):
        try:
            config_option = self.config[item]
            if config_option == None:
                return self.load_defaults(item)
            else:
                if item == "time_series_intervals":
                    config_option = [i for i in config_option if i in valid_time_series_intervals]
                return config_option
        except KeyError:
            #print >> sys.stderr, "### Web Configuration Warning ###"
            #print >> sys.stderr, "The %s variable does not exist in your web_config file.cfg" % item
            #print >> sys.stderr, "If you wish to override the default value, please add it to your web_config.cfg file"
            config_option = self.load_defaults(item)
            return config_option
       
    def load_defaults(self, key):
        if key == "concordance_length":
            return 300
        elif key == "facets":
            return self.config['metadata']
        elif key == "search_reports":
            return ['concordance', 'kwic', 'collocation', 'time_series']
        elif key == "metadata_aliases":
            return {}
        elif key == "time_series_intervals":
            return [10, 50, 100]
        elif key == "theme":
            return "default_theme.css"
        else:
            return False
        
    def JSONify(self):
        config_obj = dict([(option, self[option]) for option in self.options])
        return dumps(config_obj)
