#!/usr/bin/env python3

import os
import re
import subprocess
import sys
import unicodedata
from wsgiref.handlers import CGIHandler

import json
from philologic.DB import DB
from philologic.MetadataQuery import metadata_pattern_search
from philologic.QuerySyntax import parse_query

from philologic.runtime import WebConfig
from philologic.runtime import WSGIHandler

environ = os.environ
environ["PATH"] += ":/usr/local/bin/"
environ["LANG"] = "C"


def metadata_list(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),
               ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace('scripts', ''))
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(environ, config)
    metadata = request.term
    field = request.field
    yield autocomplete_metadata(metadata, field, db).encode('utf8')

def autocomplete_metadata(metadata, field, db):
    path = os.environ['SCRIPT_FILENAME'].replace('scripts/metadata_list.py',
                                                 '')
    path += 'data/frequencies/%s_frequencies' % field

    ## Workaround for when jquery sends a list of words: this happens when using the back button
    if isinstance(metadata, list):
        metadata = metadata[-1]
        field = field[-1]

    words = format_query(metadata, field, db)[:100]
    return json.dumps(words)


def format_query(q, field, db):
    parsed = parse_query(q)
    parsed_split = []
    unique_matches = set()
    for label, token in parsed:
        l, t = label, token
        if l == "QUOTE":
            if t[-1] != '"':
                t += '"'
            subtokens = t[1:-1].split("|")
            parsed_split += [("QUOTE_S", sub_t) for sub_t in subtokens
                             if sub_t]
        elif l == "RANGE":
            parsed_split += [("TERM", t)]
        else:
            parsed_split += [(l, t)]
    output_string = []
    label, token = parsed_split[-1]
    prefix = " ".join('"' + t[1] + '"' if t[0] == "QUOTE_S" else t[1]
                      for t in parsed_split[:-1])
    if prefix:
        prefix = prefix + " CUTHERE "
    expanded = []
    if label == "QUOTE_S" or label == "TERM":
        norm_tok = token.decode("utf-8").lower()
        norm_tok = [i
                    for i in unicodedata.normalize("NFKD", norm_tok)
                    if not unicodedata.combining(i)]
        norm_tok = "".join(norm_tok).encode("utf-8")
        matches = metadata_pattern_search(
            norm_tok, db.locals.db_path +
            "/data/frequencies/normalized_%s_frequencies" % field)
        substr_token = token.decode("utf-8").lower().encode("utf-8")
        exact_matches = exact_word_pattern_search(
            substr_token + '.*',
            db.locals.db_path + "/data/frequencies/%s_frequencies" % field)
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


def exact_word_pattern_search(term, path):
    command = ['egrep', '-awie', "[[:blank:]]?" + term, path]
    grep = subprocess.Popen(command, stdout=subprocess.PIPE, env=environ)
    cut = subprocess.Popen(["cut", "-f", "1"],
                           stdin=grep.stdout,
                           stdout=subprocess.PIPE)
    match, stderr = cut.communicate()
    matches = [i for i in match.split('\n') if i]
    return matches


def highlighter(words, norm_tok, substr_tok):
    new_list = []
    token_len = len(norm_tok)
    for word in words:
        highlighted_section = word.decode('utf8')[:token_len]
        end_word = word.decode('utf-8')[token_len:]
        highlighted_word = '<span class="highlight">' + highlighted_section + '</span>' + end_word
        new_list.append(highlighted_word.encode('utf8'))
    return new_list


if __name__ == "__main__":
    CGIHandler().run(metadata_list)
