#! /usr/bin/env python

import os
import sys
try:
    import simplejson as json
except ImportError:
    print >> sys.stderr, "Please install simplejson for better performance"
    import json
from philologic.DB import DB
from philologic.Config import MakeWebConfig
from search_utilities import search_examples

valid_time_series_intervals = set([1, 10, 50, 100])


def WebConfig():
    db_path = os.path.abspath(os.path.dirname(__file__)).replace('functions', '')
    return MakeWebConfig(db_path + '/data/web_config.cfg')
