#!/usr/bin/env python

import os
import cgi
import sys
sys.path.append('..')
import json
import subprocess
import re
import unicodedata
from wsgiref.handlers import CGIHandler
from philologic.QuerySyntax import parse_query
from philologic.Query import word_pattern_search
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

def highlighter(words, token_len):
    highlighted_matches = []
    for word in words:
        highlighted_section = word.decode('utf-8')[:token_len]
        end_word = word.decode('utf-8')[token_len:]
        h_word = u'<span class="highlight">' + highlighted_section + '</span>' + end_word
        h_word = h_word.encode('utf-8')
        highlighted_matches.append(h_word)
    return highlighted_matches

def format_query(q, db):
    parsed = parse_query(q)
    parsed_split = []
    for label,token in parsed:
        l,t = label,token
        if l == "QUOTE":
            if t[-1] != '"':
                t += '"'
            subtokens = t[1:-1].split(" ")
            parsed_split += [("QUOTE_S",sub_t) for sub_t in subtokens if sub_t]
        else:
            parsed_split += [(l,t)]
    output_string = []
    label, token = parsed_split[-1]
    prefix = " ".join('"'+t[1]+'"' if t[0] == "QUOTE_S" else t[1] for t in parsed_split[:-1])
    if prefix:
        prefix = prefix + " "
    expanded = []
    if label == "QUOTE_S" or label == "TERM":
        norm_tok = token.decode("utf-8").lower()
        norm_tok = [i for i in unicodedata.normalize("NFKD",norm_tok) if not unicodedata.combining(i)]
        norm_tok = "".join(norm_tok).encode("utf-8")
        matches = word_pattern_search(norm_tok,db.locals["db_path"]+"/frequencies/normalized_word_frequencies")
        substr_token = token.decode("utf-8").lower().encode("utf-8")
        exact_matches = exact_word_pattern_search(substr_token + '.*',db.locals["db_path"]+"/frequencies/word_frequencies")
        for m in exact_matches:
            if m not in matches:
                matches.append(m)
        matches = highlighter(matches, len(norm_tok))
        for m in matches:
            if label == "QUOTE_S":
                output_string.append(prefix + '"%s"' % m)
            else:
                output_string.append(prefix + m)
    return output_string

def autocomplete_term(q, db):
    ## Workaround for when jquery send a list of words: happens when using the back button
    if isinstance(q, list):
        q = q[-1]
    all_words = format_query(q, db)[:100] 
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
    
