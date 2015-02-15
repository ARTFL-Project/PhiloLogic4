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
from wsgiref.handlers import CGIHandler
from functions.wsgi_handler import WSGIHandler
from functions.ObjectFormatter import adjust_bytes, convert_entities
from functions.FragmentParser import strip_tags

## Precompiled regexes for performance
left_truncate = re.compile (r"^\w+", re.U)
right_truncate = re.compile("\w+$", re.U)
word_identifier = re.compile(r"\w", re.U)

begin_match = re.compile(r'^[^<]*?>')
start_cutoff_match = re.compile(r'^[^ <]+')
end_match = re.compile(r'<[^>]*?\Z')


def collocation(environ,start_response):
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response('200 OK',headers)
    hits = db.query(request["q"],request["method"],request["arg"],**request.metadata)
    collocation_object = fetch_collocation(hits, request, db, config)
    yield json.dumps(collocation_object)

def fetch_collocation(hits, q, db, config):
    collocation_object = {"query": dict([i for i in q]), "results_length": len(hits)}
    
    length = config['concordance_length']
    try:
        within_x_words = int(q['word_num'])
    except ValueError: ## Getting an empty string since the keyword is not specificed in the URL
        within_x_words = 5
    
    if q.colloc_filter_choice == "nofilter":
        filter_list = []
    else:
        filter_list = build_filter_list(q, config)
    collocation_object['filter_list'] = list(filter_list)
        
    
    ## start going though hits ##
    left_collocates = {}
    right_collocates = {}
    all_collocates = {}
        
    ## Remove all empty keywords in request object
    new_q = []
    for i in q:
        if i[1]:
            new_q.append(i)
    
    count = 0
    
    for hit in hits[q.start:q.end]:
        conc_left, conc_right = split_concordance(hit, length, config.db_path)
        left_words = tokenize(conc_left, filter_list, within_x_words, 'left', db)
        right_words = tokenize(conc_right, filter_list, within_x_words, 'right', db)
        
        for left_word in left_words:
            try:
                left_collocates[left_word]['count'] += 1
            except KeyError:
                left_collocates[left_word] = {"count": 1, "url": f.link.make_absolute_query_link(config, new_q, report="concordance_from_collocation", direction="left", collocate=left_word.encode('utf-8'))}
            try:
                all_collocates[left_word]['count'] += 1
            except KeyError:
                all_collocates[left_word] = {"count": 1, "url": f.link.make_absolute_query_link(config, new_q, report="concordance_from_collocation", direction="all", collocate=left_word.encode('utf-8'))}

        for right_word in right_words:
            try:
                right_collocates[right_word]['count'] += 1
            except KeyError:
                right_collocates[right_word] = {"count": 1, "url": f.link.make_absolute_query_link(config, new_q, report="concordance_from_collocation", direction="right", collocate=right_word.encode('utf-8'))}
            try:
                all_collocates[right_word]['count'] += 1
            except KeyError:
                all_collocates[right_word] = {"count": 1, "url": f.link.make_absolute_query_link(config, new_q, report="concordance_from_collocation", direction="all", collocate=right_word.encode('utf-8'))}
    
    collocation_object['all_collocates'] = all_collocates
    collocation_object['left_collocates'] = left_collocates
    collocation_object['right_collocates'] = right_collocates
    
    return collocation_object

def build_filter_list(q, config):
    ## set up filtering with stopwords or most frequent terms ##
    if config.stopwords and q.colloc_filter_choice == "stopwords":
        filter_file = open(config.stopwords)
        filter_num = float("inf")
    else:
        filter_file = open(config.db_path + '/data/frequencies/word_frequencies')
        if q.filter_frequency:
            filter_num = int(q.filter_frequency)
        else:
            filter_num = 100 ## default value in case it's not defined
    filter_list = set([q['q'].decode("utf-8")])
    for line_count, line in enumerate(filter_file):
        if line_count == filter_num:
            break
        try:
            word = line.split()[0]
        except IndexError:
            continue
        filter_list.add(word.decode('utf-8', 'ignore'))
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
    token_regex_pattern = db.locals["word_regex"] + u'|' + db.locals["punct_regex"]
    token_regex = re.compile(token_regex_pattern, re.U)
    if direction == 'left':
        word_list = tokenize_text(text, token_regex) 
        word_list.reverse() ## left side needs to be reversed
    else:
        word_list = tokenize_text(text, token_regex)
      
    word_list = filter(word_list, filter_list, within_x_words)
    return word_list

def filter(word_list, filter_list, within_x_words):
    words_to_pass = []
    for word in word_list[:within_x_words]:
        if word not in filter_list and word_identifier.search(word):
            words_to_pass.append(word)
    return words_to_pass

def tokenize_text(text, token_regex):
    """Returns a list of individual tokens"""
    ## Still used in collocations
    text_tokens = token_regex.split(text)
    text_tokens = [token for token in text_tokens if token and token not in (""," ","\n","\t")] ## remove empty strings
    return text_tokens

if __name__ == "__main__":
    CGIHandler().run(collocation)