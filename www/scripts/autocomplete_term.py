#!/usr/bin/env python

import os
import cgi
import sys
sys.path.append('..')
import functions as f
import json
import subprocess
from wsgiref.handlers import CGIHandler
from philologic.QuerySyntax import parse_query, group_terms
from philologic.Query import split_terms, grep_word
from philologic.DB import DB
from functions.wsgi_handler import WSGIHandler


def term_list(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'), ("Access-Control-Allow-Origin","*")]
    start_response(status, headers)
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    term = request.term
    if isinstance(term, list):
        term = term[-1]
    all_words = format_query(term, db, config)[:100]
    yield json.dumps(all_words)

def format_query(q, db, config):
    parsed = parse_query(q)
    group = group_terms(parsed)
    all_groups = split_terms(group)

    # We extract every word tuple
    word_groups = []
    for g in all_groups:
        for inner_g in g:
            word_groups.append(inner_g)
    last_group = word_groups.pop()  # we take the last tuple for autocomplete
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
    frequency_file = config.db_path +"/data/frequencies/normalized_word_frequencies"

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

def highlighter(word, token_len):
    highlighted_section = word.decode('utf-8')[:token_len]
    end_word = word.decode('utf-8')[token_len:]
    highlighted_word = u'<span class="highlight">' + highlighted_section + '</span>' + end_word
    highlighted_word = highlighted_word.encode('utf-8')
    return highlighted_word

if __name__ == "__main__":
    CGIHandler().run(term_list)

