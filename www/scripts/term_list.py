#!/usr/bin/env python

import os
import cgi
import sys
sys.path.append('..')
from functions.query_parser import *
import json

    
def autocomplete_term(word_start):
    path = os.environ['SCRIPT_FILENAME'].replace('scripts/term_list.py', '')
    path += 'data/frequencies/normalized_word_frequencies'
    
    ## Workaround for when jquery send a list of words: happens when using the back button
    if isinstance(word_start, list):
        word_start = word_start[-1]
        
    word_start +='*'
    words = word_pattern_search(word_start, path)[:10]
    return json.dumps(words)

if __name__ == "__main__":
    form = cgi.FieldStorage()
    term = form.getvalue('term')
    content = autocomplete_term(term)
    print "Content-Type: text/html\n"
    print content
    