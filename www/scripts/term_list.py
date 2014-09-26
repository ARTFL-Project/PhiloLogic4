#!/usr/bin/env python

import os
import cgi
import sys
sys.path.append('..')
import json
import subprocess
import re
import unicodedata
import urlparse
from wsgiref.handlers import CGIHandler
from philologic.QuerySyntax import parse_query, group_terms
from philologic.Query import word_pattern_search, split_terms, grep_word
from functions.wsgi_handler import parse_cgi


def exact_word_pattern_search(term, path):
    command = ['egrep', '-iw', "^%s" % term, '%s' % path]
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    match, stderr = process.communicate()
    match = match.split('\n')
    match.remove('')
    ## HACK: The extra decode/encode are there to fix errors when this list is converted to a json object
    matches = [m.split()[0].strip().decode('utf-8', 'ignore').encode('utf-8') for m in match]
    return matches

def highlighter(word, token_len):
    highlighted_section = word.decode('utf-8')[:token_len]
    end_word = word.decode('utf-8')[token_len:]
    highlighted_word = u'<span class="highlight">' + highlighted_section + '</span>' + end_word
    highlighted_word = highlighted_word.encode('utf-8')
    return highlighted_word

def format_query(q, db):
    parsed = parse_query(q)
    group = group_terms(parsed)
    all_groups = split_terms(group)
    
    # We extract every word tuple
    word_groups = []
    for g in all_groups:
        for inner_g in g:
            word_groups.append(inner_g)
    last_group = word_groups.pop()  ## we take the last tuple for autocomplete
    token = last_group[1]
    kind = last_group[0]
    if word_groups:
        prefix = ' '.join([i[1] for i in word_groups]) + " "
    else:
        prefix = ''

    if kind == "OR":
        return []
    if kind == "QUOTE":
        token = token.replace('"', '')
    frequency_file = db.locals["db_path"]+"/frequencies/normalized_word_frequencies"
    
    expanded_token = token + '.*'
    grep_proc = grep_word(expanded_token, frequency_file, subprocess.PIPE)
    
    matches = []
    len_token = len(token.decode('utf-8'))
    for line in grep_proc.stdout:
        word = line.split('\t')[1]
        highlighted_word = highlighter(word, len_token)
        matches.append(highlighted_word)

    output_string = []
    for m in matches:
        if kind == "QUOTE":
            output_string.append(prefix + '"%s"' % m)
        else:
            output_string.append(prefix +  m)
    
    return output_string

def autocomplete_term(q, db):
    ## Workaround for when jquery send a list of words: happens when using the back button
    if isinstance(q, list):
        q = q[-1]
    all_words = format_query(q, db)[:100]
    print >> sys.stderr, "AUTOCOMP", repr(all_words)
    return json.dumps(all_words)

def term_list(environ,start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    environ["SCRIPT_FILENAME"] = environ["SCRIPT_FILENAME"].replace('scripts/term_list.py', '')
    db, path_components, q = parse_cgi(environ)
    cgi = urlparse.parse_qs(environ["QUERY_STRING"],keep_blank_values=True)
    term = cgi.get('term',[''])[0]
    yield autocomplete_term(term,db)

if __name__ == "__main__":
    CGIHandler().run(term_list)
    
