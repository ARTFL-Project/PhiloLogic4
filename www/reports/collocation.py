#!/usr/bin/env python

import sys
sys.path.append('..')
import functions as f
import reports as r
import os
import re
import json
import unicodedata
from philologic.DB import DB
from functions.wsgi_handler import WSGIHandler
from functions.ObjectFormatter import adjust_bytes, convert_entities
from functions.FragmentParser import strip_tags
from collections import defaultdict
from operator import itemgetter

## Precompiled regexes for performance
left_truncate = re.compile (r"^\w+", re.U)
right_truncate = re.compile("\w+$", re.U)
word_identifier = re.compile("\w", re.U)

begin_match = re.compile(r'^[^<]*?>')
start_cutoff_match = re.compile(r'^[^ <]+')
end_match = re.compile(r'<[^>]*?\Z')


def collocation(environ,start_response):
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    if request.no_q:
        return r.fetch_bibliography(db, request, config, start_response)
    hits = db.query(request["q"],request["method"],request["arg"],**request.metadata)
    headers = [('Content-type', 'text/html; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response('200 OK',headers)
    return render_collocation(hits, db, request, config)
    
def render_collocation(hits, db, q, config):
    collocation_object = fetch_collocation(hits, q, db, config)
    biblio_criteria = f.biblio_criteria(q, config)
    return f.render_template(collocation=collocation_object, query_string=q.query_string, biblio_criteria=biblio_criteria,
                             word_num=q.word_num, config=config, dumps=json.dumps, template_name='collocation.mako', report="collocation")

def fetch_collocation(hits, q, db, config, word_filter=True, filter_num=100, full_report=True, stopwords=True):
    collocation_object = {"query": dict([i for i in q]), "results_length": len(hits)}
    
    length = config['concordance_length']
    within_x_words = int(q['word_num'])
    
    filter_list = build_filter_list(word_filter, stopwords, filter_num, q, config.db_path)
    
    ## start going though hits ##
    left_collocates = defaultdict(int)
    right_collocates = defaultdict(int)
    all_collocates = defaultdict(int)
    
    count = 0
    for hit in hits[q.interval_start:q.interval_end]:
        conc_left, conc_right = split_concordance(hit, length, config.db_path)
        left_words = tokenize(conc_left, filter_list, within_x_words, 'left', db)
        right_words = tokenize(conc_right, filter_list, within_x_words, 'right', db)
        
        for l_word in left_words:
            left_collocates[l_word] += 1
            all_collocates[l_word] += 1 

        for r_word in right_words:
            right_collocates[r_word] += 1
            all_collocates[r_word] += 1  
    
    collocation_object['all_collocates'] = all_collocates
    collocation_object['left_collocates'] = left_collocates
    collocation_object['right_collocates'] = right_collocates
    
    return collocation_object

def build_filter_list(word_filter, stopwords, filter_num, q, path):
    ## set up filtering with stopwords or 100 most frequent terms ##
    filter_list = set([q['q']])
    if word_filter:
        if stopwords:
            filter_list_path = path + '/data/stopwords.txt'
            if os.path.isfile(filter_list_path):
                filter_words_file = open(filter_list_path)
                filter_num = float("inf")
            else:
                filter_list_path = path + '/data/frequencies/word_frequencies'
                filter_words_file = open(filter_list_path)
        else:
            filter_list_path = path + '/data/frequencies/word_frequencies'
            filter_words_file = open(filter_list_path)
        line_count = 0 
        for line in filter_words_file:
            line_count += 1
            try:
                word = line.split()[0]
            except IndexError:
                continue
            filter_list.add(word.decode('utf-8', 'ignore'))
            if line_count > filter_num:
                break
    return filter_list

def split_concordance(hit, length, path):
    bytes, byte_start = adjust_bytes(hit.bytes, length)
    conc_text = f.get_text(hit, byte_start, length, path)
    
    ## Isolate left and right concordances
    conc_left = convert_entities(conc_text[:bytes[0]].decode('utf-8', 'ignore'))
    conc_left = begin_match.sub('', conc_left)
    conc_left = start_cutoff_match.sub('', conc_left)
    conc_right = convert_entities(conc_text[bytes[-1]:].decode('utf-8', 'ignore'))
    conc_right = end_match.sub('', conc_right)
    conc_right = left_truncate.sub('', conc_right)
    conc_left = strip_tags(conc_left)
    conc_right = strip_tags(conc_right)
    
    return conc_left, conc_right


def tokenize(text, filter_list, within_x_words, direction, db):
    text = text.lower()
    token_regex = re.compile(db.locals['word_regex'] + '|' + db.locals['punct_regex'], re.U)
    
    if direction == 'left':
        word_list = tokenize_text(text, token_regex) 
        word_list.reverse() ## left side needs to be reversed
    else:
        word_list = tokenize_text(text, token_regex)
      
    word_list = filter(word_list, filter_list, within_x_words)

    return word_list

def filter(word_list, filter_list, within_x_words):

    ## this code currently presumes filtering -- I append only non-filter words ##
    ## also, I check to make sure there are actual characters in my word -- no empties, please ##
    ## character set can be extended, of course ##

    words_to_pass = []
    for word in word_list[:within_x_words]:
        if word not in filter_list and word_identifier.search(word):
            words_to_pass.append(word)
    return words_to_pass

def tokenize_text(text, token_regex):
    """Returns a list of individual tokens"""
    ## Still used in collocations
    text_tokens = token_regex.split(text)
    text_tokens = [token for token in text_tokens if token and re.search('\w', token)] ## remove empty strings
    return text_tokens