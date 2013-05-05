#!/usr/bin/env python

import sys
sys.path.append('..')
import functions as f
import os
import re
import json
from functions.wsgi_handler import wsgi_response
from render_template import render_template
from functions.format import adjust_bytes, clean_text, chunkifier, tokenize_text
from bibliography import bibliography
from collections import defaultdict

## Precompiled regexes for performance
left_truncate = re.compile ("^[^\s]* ")
right_truncate = re.compile(" [^\s]*$")
word_identifier = re.compile("[a-z\xa0-\xc3]")


def collocation(environ,start_response):
    db, dbname, path_components, q = wsgi_response(environ,start_response)
    path = os.getcwd().replace('functions/', '')
    if q['q'] == '':
        return bibliography(f,path, db, dbname,q,environ) ## the default should be an error message
    hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
    all_colloc, left_colloc, right_colloc = fetch_collocation(hits, path, q)
    hit_len = len(hits)
    return render_template(all_colloc=all_colloc, left_colloc=left_colloc, right_colloc=right_colloc,
                           db=db,dbname=dbname,q=q,link=link_to_concordance,f=f,path=path,
                           results_per_page=q['results_per_page'],hit_len=hit_len,
                           order=sort_to_display,dumps=json.dumps,template_name='collocation.mako')

def fetch_collocation(results, path, q, word_filter=True, filter_num=200, full_report=True):
    within_x_words = q['word_num']    
    
    ## set up filtering of most frequent 200 terms ##
    filter_list = set([])
    if word_filter:
        filter_list_path = path + '/data/frequencies/word_frequencies'
        filter_words_file = open(filter_list_path)
        line_count = 0 
        for line in filter_words_file:
            line_count += 1
            word = line.split()[0]
            filter_list.add(word.decode('utf-8', 'ignore'))
            if line_count > filter_num:
                    break
    
    ## start going though hits ##
    left_collocates = defaultdict(int)
    right_collocates = defaultdict(int)
    all_collocates = defaultdict(int)
    
    count = 0
    if not full_report:
        q['colloc_start'] = None
        q['colloc_end'] = None
    for hit in results[q['colloc_start']:q['colloc_end']]:
        ## get my chunk of text ##
        bytes, byte_start = adjust_bytes(hit.bytes, 400)
        conc_text = f.get_text(hit, byte_start, 400, path)
        conc_left, conc_middle, conc_right = chunkifier(conc_text, bytes)
        
        left_words = tokenize(conc_left, filter_list, within_x_words, 'left')
        right_words = tokenize(conc_right, filter_list, within_x_words, 'right')
        
        query_words = set([w.decode('utf-8') for w in q['q'].split('|')])
        
        for l_word in left_words:
            if l_word in query_words:
                continue
            left_collocates[l_word] += 1
            all_collocates[l_word] += 1 

        for r_word in right_words:
            if r_word in query_words:
                continue
            right_collocates[r_word] += 1
            all_collocates[r_word] += 1    

    if full_report:
        return dict(all_collocates), dict(left_collocates), dict(right_collocates)
    else:
        return sorted(all_collocates.items(), key=lambda x: x[1], reverse=True)

def tokenize(text, filter_list, within_x_words, direction, highlighting=False):
    text = clean_text(text, collocation=True)
    text = text.lower()
    
    if direction == 'left':
        text = left_truncate.sub("", text) ## hack off left-most word (potentially truncated)
        word_list = tokenize_text(text) 
        word_list.reverse() ## left side needs to be reversed
    else:
        text = right_truncate.sub("", text) ## hack off right-most word (potentially truncated)
        word_list = tokenize_text(text)
      
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

def sort_to_display(all_collocates, left_collocates, right_collocates):
    left_colloc = sorted(left_collocates.items(), key=lambda x: x[1], reverse=True)[:100]
    right_colloc = sorted(right_collocates.items(), key=lambda x: x[1], reverse=True)[:100]
    all_colloc = sorted(all_collocates.items(), key=lambda x: x[1], reverse=True)[:100]
    return zip(all_colloc, left_colloc, right_colloc)
    

def link_to_concordance(q, collocate, direction, collocate_num):
    collocate_values = [collocate.encode('utf-8', 'ignore'), direction, q['word_num'], collocate_num]
    return f.link.make_query_link(q['q'], method=q['method'], arg=q['arg'], report="concordance_from_collocation",
                                  collocate=collocate_values,**q['metadata'])
    

