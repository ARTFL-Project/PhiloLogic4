#!/usr/bin/env python

import os
import cgi
import sys
import json
import re
import subprocess
sys.path.append('..')

def highlighter(words, metadata):
    new_list = []
    for word in words:
        regex = re.compile(r'(%s)' % metadata, re.I)
        w = regex.sub('<span class="highlight">\\1</span>', word)
        new_list.append(w)
    return new_list
  
def metadata_pattern_search(term, path):
    term = '(.* |^)%s.*' % term
    command = ['egrep', '-oie', "%s\W" % term, '%s' % path]
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    match, stderr = process.communicate()
    return [m.strip() for m in match.split('\n')]

def autocomplete_metadata(metadata, field):
    path = os.environ['SCRIPT_FILENAME'].replace('scripts/metadata_list.py', '')
    path += 'data/frequencies/%s_frequencies' % field
    
    ## Workaround for when jquery sends a list of words: this happens when using the back button
    if isinstance(metadata, list):
        metadata = metadata[-1]
        field = field[-1]    

    words = metadata_pattern_search(metadata, path)
    words = highlighter(words, metadata)
    return json.dumps(words)

if __name__ == "__main__":
    form = cgi.FieldStorage()
    metadata = form.getvalue('term')
    field = form.getvalue('field')
    content = autocomplete_metadata(metadata, field)
    print "Content-Type: text/html\n"
    print content
    