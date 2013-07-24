#!/usr/bin/env python

import os
import cgi
import sys
sys.path.append('..')
import json
import subprocess
import re
import unicodedata
from philologic.QuerySyntax import parse_query
from philologic.Query import word_pattern_search
from functions.wsgi_handler import parse_cgi


def exact_word_pattern_search(token, path):
    term = token[:] + '.*'
    command = ['egrep', '-ie', "^%s\s" % term, '%s' % path]
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    match, stderr = process.communicate()
    match = match.split('\n')
    match.remove('')
    ## HACK: The extra decode/encode are there to fix errors when this list is converted to a json object
    matches = [m.split()[0].strip().decode('utf-8', 'ignore').encode('utf-8') for m in match]
    return highlighter(matches, token)

def highlighter(words, token):
    token_len = len(token)
    highlighted_matches = []
    for word in words:
        highlighted_section = word.decode('utf-8')[:token_len]
        end_word = word.decode('utf-8')[token_len:]
        h_word = u'<span class="highlight">' + highlighted_section + '</span>' + end_word
        h_word = h_word.encode('utf-8')
        highlighted_matches.append(h_word)
    return highlighted_matches

def format_query(q, db):
    parsed_split = []
    for word in q.split():
        if word.startswith('"'):
            parsed_split.append(("QUOTE_S", word.replace('"', '')))
        else:
            parsed_split.append(("TERM", word))
    output_string = []
    label, token = parsed_split[-1]
    expanded = []
    if label == "QUOTE_S":
        token = token.decode("utf-8").lower().encode("utf-8")
        matches = exact_word_pattern_search(token,db.locals["db_path"]+"/frequencies/word_frequencies")
    elif label == "TERM":
        norm_tok = token.decode("utf-8").lower()
        norm_tok = [i for i in unicodedata.normalize("NFKD",norm_tok) if not unicodedata.combining(i)]
        norm_tok = "".join(norm_tok).encode("utf-8")
        matches = word_pattern_search(norm_tok + '.*',db.locals["db_path"]+"/frequencies/normalized_word_frequencies")
        matches = highlighter(matches, norm_tok.decode('utf-8'))
    for m in matches:
        if m not in expanded:
            expanded += [m.strip()]                                              
    output_string += expanded
    if len(q) > 1:
        mod_output = []
        for s in output_string:
            new_s = ''.join(re.split('([ |])', q)[:-1] + [s.strip()])
            mod_output.append(new_s.strip())
        return mod_output
    else:
        return output_string

def autocomplete_term(q, db):
    ## Workaround for when jquery send a list of words: happens when using the back button
    if isinstance(q, list):
        q = q[-1]
    all_words = format_query(q, db)[:100] 
    return json.dumps(all_words)

if __name__ == "__main__":
    environ = os.environ
    environ["SCRIPT_FILENAME"] = environ["SCRIPT_FILENAME"].replace('scripts/term_list.py', '')
    db, path_components, q = parse_cgi(environ)
    form = cgi.FieldStorage()
    term = form.getvalue('term')
    content = autocomplete_term(term, db)
    print "Content-Type: text/html\n"
    print content
    