#! /usr/bin/env python

import os


class WebConfig(object):
    
    def __init__(self, db_locals):
        self.db_locals = db_locals
        self.config = {}
        path = os.getcwd().replace('functions', "") + "/data/web_config.cfg"
        execfile(path, globals(), self.config)
    
    def __getattr__(self, attr):
        try:
            return self.config[attr]
        except KeyError:
            config = defaults(attr)
            if config :
                return load_defaults(attr)
            else:
                raise AttributeError
    
    def __getitem__(self, item):
        try:
            return self.config[item]
        except KeyError:
            config = load_defaults(item)
            if config:
                return config
            else:
                raise KeyError
    
    def load_defaults(self, key):
        if key == "concordance_length":
            return 300
        elif key == "facets":
            return self.db_locals['metadata_fields']
        elif key == "search_reports":
            return ['concordance', 'kwic', 'collocation', 'time_series']
        elif key == "metadata_aliases":
            return {}
        elif key == "metadata":
            return self.db_locals['metadata_fields']
        else:
            try:
                return self.db_locals[key]
            except KeyError:
                return False
