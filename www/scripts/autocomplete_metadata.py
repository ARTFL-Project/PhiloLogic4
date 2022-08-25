#!/usr/bin/env python3

import os
import subprocess
import sys
from wsgiref.handlers import CGIHandler

import orjson
import regex as re
from philologic.runtime.DB import DB
from philologic.runtime.MetadataQuery import metadata_pattern_search
## parse_query now resides in this script ##
#from philologic.runtime.QuerySyntax import parse_query
from unidecode import unidecode

sys.path.append("..")
import custom_functions

try:
    from custom_functions import WebConfig
except ImportError:
    from philologic.runtime import WebConfig
try:
    from custom_functions import WSGIHandler
except ImportError:
    from philologic.runtime import WSGIHandler

environ = os.environ
environ["PATH"] += ":/usr/local/bin/"
environ["LANG"] = "C"

patterns = [
    ("QUOTE", r'".+?"'),
    ("QUOTE", r'".+'),
    ("NOT", "NOT"),
    ("OR", r"\|"),
    ("RANGE", r"[^|\s]+?\-[^|\s]+"),
    ("RANGE", r"\d+\-\Z"),
    ("RANGE", r"\-\d+\Z"),
    ("NULL", r"NULL"),
    ("TERM", r'[^\-|"]+'), ## cmc removing space here to prevent confusing search suggestions ##
]

## using this for search highlighting -- to match 
accented_roman_chars = re.compile(r'[\u00c0-\u0174]')

def metadata_list(environ, start_response):
    """Retrieve metadata list"""
    status = "200 OK"
    headers = [("Content-type", "application/json; charset=UTF-8"), ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace("scripts", ""))
    db = DB(config.db_path + "/data/")
    request = WSGIHandler(environ, config)
    metadata = request.term
    field = request.field
    yield autocomplete_metadata(metadata, field, db)


def autocomplete_metadata(metadata, field, db):
    """Autocomplete metadata"""
    path = os.environ["SCRIPT_FILENAME"].replace("scripts/metadata_list.py", "")
    path += "data/frequencies/%s_frequencies" % field

    ## Workaround for when jquery sends a list of words: this happens when using the back button
    if isinstance(metadata, list):
        metadata = metadata[-1]
        field = field[-1]

    words = format_query(metadata, field, db)[:100]
    return orjson.dumps(words)    
    

def format_query(q, field, db):
    """Format query"""
    parsed = parse_query(q)
    #print("PARSED: ", parsed, file=sys.stderr)
    parsed_split = []
    for label, token in parsed:
        l, t = label, token
        if l == "QUOTE":
            if t[-1] != '"':
                t += '"'
            subtokens = t[1:-1].split("|")
            parsed_split += [("QUOTE_S", sub_t) for sub_t in subtokens if sub_t]
        elif l == "RANGE":
            parsed_split += [("TERM", t)]
        else:
            parsed_split += [(l, t)]
    output_string = []
    label, token = parsed_split[-1]
    prefix = " ".join('"' + t[1] + '"' if t[0] == "QUOTE_S" else t[1] for t in parsed_split[:-1])
    if prefix:
        prefix = prefix + " CUTHERE "
    if label == "QUOTE_S" or label == "TERM":
        norm_tok = token.lower()
        if db.locals.ascii_conversion is True:
            norm_tok = unidecode(norm_tok)
        norm_tok = "".join(norm_tok).encode("utf-8")
        
        ## it's not clear that metadata_pattern_search generates suggestions... ##
        matches = metadata_pattern_search(
            norm_tok, db.locals.db_path + "/data/frequencies/normalized_%s_frequencies" % field
            )
        
        ## ... so I'm going to keep all the code local and use only this function, ##
        ## leaving its name as is even though it generates exact and term matches. ##
        ## NOTE -- I'm sending label to be able to differentiate between QUOTE_S  ##
        ## and TERM matches. I'm also sending ascii_conversion to keep from doing ##
        ## potential damage to non-latin character sets. Not sure I actually need it ##
        ## but I'm doing it anyway... ##
        
        substr_token = token.lower()
        exact_matches = exact_word_pattern_search(
            substr_token + ".*", db.locals.db_path + "/data/frequencies/", field, label, db.locals.ascii_conversion
            )
        for m in exact_matches:
            if m not in matches:
                matches.append(m)
        matches = highlighter(matches, token, db.locals.ascii_conversion) ## sending token instead of norm_tok
        for m in matches:
            if label == "QUOTE_S":
                output_string.append(prefix + '"%s"' % m)
            else:
                if re.search(r"\|", m):
                    m = '"' + m + '"'
                output_string.append(prefix + m)
                
    return output_string

def parse_query(qstring):
    """Parse query"""
    buf = qstring[:]
    parsed = []
    while len(buf) > 0:
        for label, pattern in patterns:
            m = re.match(pattern, buf)
            if m:
                parsed.append((label, m.group()))
                buf = buf[m.end() :]
                break
        else:
            buf = buf[1:]
    return parsed

def exact_word_pattern_search(term, path, field, label, ascii_conversion):
    """Exact word pattern search"""
    
    ## note that all match results will be in the original form, ie, not flattened ##
    ## or stripped of accents ##
    
    if label == "TERM":
        norm_term = term.lower() 
        path = path + "normalized_%s_frequencies" % field
        command = ["egrep", "-awie", "[[:blank:]]?" + norm_term, path]
        grep = subprocess.Popen(command, stdout=subprocess.PIPE, env=environ)
        cut = subprocess.Popen(["cut", "-f", "2"], stdin=grep.stdout, stdout=subprocess.PIPE)
        match, _ = cut.communicate()
        matches = [i.decode("utf8") for i in match.split(b"\n") if i]
    
    elif label == "QUOTE_S":
        path = path + "%s_frequencies" % field
        command = ["egrep", "-awie", "^" + term, path]
        grep = subprocess.Popen(command, stdout=subprocess.PIPE, env=environ)
        cut = subprocess.Popen(["cut", "-f", "1"], stdin=grep.stdout, stdout=subprocess.PIPE)
        match, _ = cut.communicate()
        matches = [i.decode("utf8") for i in match.split(b"\n") if i]
   
    return matches

def highlighter(words, token, ascii_conversion):
    """Highlight autocomplete"""
    new_list = []
    for word in words:
        
        ## All suggestion strings will come in in their original form. ##
        ## In order to get index values of the strings for lighlighting, I need to ##
        ## find matches when query term is both accented and non-accented. ##
        ## Note that I can't just flatten across the board using unidecode because that will ##
        ## screw up non-latin character sets. ##

        if ascii_conversion is True:
            flattened_token = unidecode(token)
            flattened_suggestion = unidecode(word)
        
        ## this should handle cases where user enters accented or unaccented, lower case or ##
        ## or upper case, ie anything that doesn't match perfectly. ##
        search_chunk = re.search(token,word,re.IGNORECASE)
        if not search_chunk:
            search_chunk = re.search(flattened_token,flattened_suggestion,re.IGNORECASE)
        
        word_chunk = word[search_chunk.start():search_chunk.end()]
        highlighted_chunk = '<span class="highlight">' + word_chunk + '</span>'
        highlighted_word = word.replace(word_chunk,highlighted_chunk)
        new_list.append(highlighted_word)
    return new_list

if __name__ == "__main__":
    CGIHandler().run(metadata_list)
