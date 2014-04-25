#! /usr/bin/env python

import os
import sys

class WebConfig(object):
    
    def __init__(self):
        self.config = {}
        path = os.getcwd().replace('functions', "").replace('scripts', '').replace('reports', '') + "/data/web_config.cfg"
        try:
            execfile(path, globals(), self.config)
        except SyntaxError:
            raise SyntaxError
        self.options = set(['db_url', 'dbname', 'concordance_length', 'facets', 'metadata',
                        'search_reports', 'metadata_aliases'])
    
    def __getattr__(self, attr):
        if attr in self.options:
            try:
                config_option = self.config[attr]
                if config_option == None:
                    return self.load_defaults(attr)
                else:
                    return config_option
            except KeyError:
                #print >> sys.stderr, "### Web Configuration Warning ###"
                #print >> sys.stderr, "The %s variable does not exist in your web_config.cfg file" % attr
                #print >> sys.stderr, "If you wish to override the default value, please add it to your web_config.cfg file"
                config_option = self.load_defaults(attr)
                return config_option
        else:
            print >> sys.stderr, "### Web Configuration Error ###"
            print >> sys.stderr, 'This variable is not supported in the current code base'
            raise AttributeError
    
    def __getitem__(self, item):
        if item in self.options:
            try:
                config_option = self.config[item]
                if config_option == None:
                    return self.load_defaults(item)
                else:
                    return config_option
            except KeyError:
                #print >> sys.stderr, "### Web Configuration Warning ###"
                #print >> sys.stderr, "The %s variable does not exist in your web_config file.cfg" % item
                #print >> sys.stderr, "If you wish to override the default value, please add it to your web_config.cfg file"
                config_option = self.load_defaults(item)
                return config_option
        else:
            print >> sys.stderr, "### Web Configuration Error ###"
            print >> sys.stderr, 'This variable is not supported in the current code base'
            raise KeyError
    
    def load_defaults(self, key):
        if key == "concordance_length":
            return 300
        elif key == "facets":
            return self.config['metadata']
        elif key == "search_reports":
            return ['concordance', 'kwic', 'collocation', 'time_series']
        elif key == "metadata_aliases":
            return {}
        else:
            return False
