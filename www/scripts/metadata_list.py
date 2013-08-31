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


def exact_word_pattern_search(term, path):
    command = ['egrep', '-wie', "%s" % term, '%s' % path]
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    match, stderr = process.communicate()
    match = match.split('\n')
    match.remove('')
    ## HACK: The extra decode/encode are there to fix errors when this list is converted to a json object
    no_num = re.compile('\d+$')
    matches =  [no_num.sub('', m).strip() for m in match]
    return matches

def highlighter(words, norm_tok, substr_tok):
    new_list = []
    regex = re.compile(r'(%s|%s)' % (norm_tok, substr_tok), re.I)
    for word in words:
        w = regex.sub('<span class="highlight">\\1</span>', word)
        new_list.append(w)
    return new_list

def format_query(q, field, db):
    parsed = parse_query(q)
    parsed_split = []
    unique_matches = set()
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
        prefix = prefix + " CUTHERE "
    expanded = []
    if label == "QUOTE_S" or label == "TERM":
        norm_tok = token.decode("utf-8").lower()
        norm_tok = [i for i in unicodedata.normalize("NFKD",norm_tok) if not unicodedata.combining(i)]
        norm_tok = "".join(norm_tok).encode("utf-8")
        matches = word_pattern_search(norm_tok,db.locals["db_path"]+"/frequencies/normalized_%s_frequencies" % field)
        substr_token = token.decode("utf-8").lower().encode("utf-8")
        exact_matches = exact_word_pattern_search(substr_token + '.*',db.locals["db_path"]+"/frequencies/%s_frequencies" % field)
        for m in exact_matches:
            if m not in matches:
                matches.append(m)
        matches = highlighter(matches, norm_tok, substr_token)
        for m in matches:
            if label == "QUOTE_S":
                output_string.append(prefix + '"%s"' % m)
            else:
                if re.search('\|', m):
                    m = '"' + m + '"'
                output_string.append(prefix + m)
    return output_string

def autocomplete_metadata(metadata, field, db):
    path = os.environ['SCRIPT_FILENAME'].replace('scripts/metadata_list.py', '')
    path += 'data/frequencies/%s_frequencies' % field
    
    ## Workaround for when jquery sends a list of words: this happens when using the back button
    if isinstance(metadata, list):
        metadata = metadata[-1]
        field = field[-1]    

    words = format_query(metadata, field, db)[:100]
    return json.dumps(words)

if __name__ == "__main__":
    environ = os.environ
    environ["SCRIPT_FILENAME"] = environ["SCRIPT_FILENAME"].replace('scripts/metadata_list.py', '')
    db, path_components, q = parse_cgi(environ)
    form = cgi.FieldStorage()
    metadata = form.getvalue('term')
    field = form.getvalue('field')
    content = autocomplete_metadata(metadata, field, db)
    print "Content-Type: text/html\n"
    print content
    