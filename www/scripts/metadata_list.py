#!/usr/bin/env python

import os
import cgi
import sys
import json
sys.path.append('..')
from functions.query_parser import *
    
def autocomplete_metadata(metadata, field):
    path = os.environ['SCRIPT_FILENAME'].replace('scripts/metadata_list.py', '')
    path += 'data/frequencies/%s_frequencies' % field
    
    ## Workaround for when jquery sends a list of words: this happens when using the back button
    if isinstance(metadata, list):
        metadata = metadata[-1]
        field = field[-1]    

    words = metadata_pattern_search(metadata, path)[:10]
    return json.dumps(words)

if __name__ == "__main__":
    form = cgi.FieldStorage()
    metadata = form.getvalue('term')
    field = form.getvalue('field')
    content = autocomplete_metadata(metadata, field)
    print "Content-Type: text/html\n"
    print content
    