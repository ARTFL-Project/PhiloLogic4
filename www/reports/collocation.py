#!/usr/bin/env python

import sys
sys.path.append('..')
import functions as f
import os
import re
import json
import unicodedata
from functions.wsgi_handler import wsgi_response
from render_template import render_template
from functions.ObjectFormatter import adjust_bytes, format_strip, convert_entities
from bibliography import fetch_bibliography as bibliography
from collections import defaultdict
from operator import itemgetter
from lxml.etree import XML, XMLParser, strip_tags, tostring

## Precompiled regexes for performance
left_truncate = re.compile ("^\w+", re.U)
right_truncate = re.compile("\w+$", re.U)
word_identifier = re.compile("\w", re.U)
highlight_match = re.compile(r'<span class="highlight">[^<]*?</span>')
token_regex = re.compile(r'[\W\d]+', re.U)

begin_match = re.compile(r'^[^<]*?>')
start_cutoff_match = re.compile(r'^[^ <]+')
end_match = re.compile(r'<[^>]*?\Z')


def collocation(environ,start_response):
    db, dbname, path_components, q = wsgi_response(environ,start_response)
    path = os.getcwd().replace('functions/', '')
    if q['q'] == '':
        return bibliography(f,path, db, dbname,q,environ) ## the default should be an error message
    hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
    all_colloc, left_colloc, right_colloc = fetch_collocation(hits, path, q, db)
    hit_len = len(hits)
    return render_template(all_colloc=all_colloc, left_colloc=left_colloc, right_colloc=right_colloc,
                           db=db,dbname=dbname,q=q,f=f,path=path, results_per_page=q['results_per_page'],
                           hit_len=hit_len, order=sort_to_display,dumps=json.dumps,
                           template_name='collocation.mako', report="collocation")

def fetch_collocation(results, path, q, db, word_filter=True, filter_num=100, full_report=True):
    within_x_words = q['word_num']    
    
    ## set up filtering of most frequent 100 terms ##
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
    for hit in results[q['interval_start']:q['interval_end']]:
        bytes, byte_start = adjust_bytes(hit.bytes, 400)
        conc_text = f.get_text(hit, byte_start, 400, path)
        
        ### Isolate left and right concordances
        #conc_left = conc_text[:bytes[0]]
        #conc_left = begin_match.sub('', conc_left)
        #conc_left = start_cutoff_match.sub('', conc_left)
        #conc_right = end_match.sub('', conc_text[bytes[-1]:])
        #conc_right = left_truncate.sub('', conc_right)
        #
        ### Clean left and right concordances
        #parser = XMLParser(recover=True)
        #left_tree = XML('<div>' + conc_left, parser=parser)
        #conc_left = tostring(left_tree, method='text', encoding='utf-8').decode('utf-8', 'ignore')
        #right_tree = XML('<div>' + conc_right, parser=parser)
        #conc_right = tostring(right_tree, method='text', encoding='utf-8').decode('utf-8', 'ignore')
        
        conc_text = format_strip(conc_text, bytes)
        conc_text = convert_entities(conc_text)
        conc_text = unicodedata.normalize('NFC', conc_text)
        start_highlight = conc_text.find('<span class="highlight"')
        end_highlight = [m.end(0) for m in highlight_match.finditer(conc_text)][-1]
        conc_left = conc_text[:start_highlight]
        conc_right = conc_text[end_highlight:]
        
        left_words = tokenize(conc_left, filter_list, within_x_words, 'left', db)
        right_words = tokenize(conc_right, filter_list, within_x_words, 'right', db)
        
        for l_word in left_words:
            left_collocates[l_word] += 1
            all_collocates[l_word] += 1 

        for r_word in right_words:
            right_collocates[r_word] += 1
            all_collocates[r_word] += 1  
    
    if full_report:
        return all_collocates, left_collocates, right_collocates
    else:
        return link_to_concordance('all', q, all_collocates, limit=200)


def tokenize(text, filter_list, within_x_words, direction, db):
    text = text.lower()
    
    if direction == 'left':
        word_list = tokenize_text(text, db) 
        word_list.reverse() ## left side needs to be reversed
    else:
        word_list = tokenize_text(text, db)
      
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

def tokenize_text(text, db):
    """Returns a list of individual tokens"""
    ## Still used in collocations
    text_tokens = token_regex.split(text)
    text_tokens = [token for token in text_tokens if token] ## remove empty strings
    return text_tokens

def sort_to_display(all_collocates, left_collocates, right_collocates):
    left_colloc = sorted(left_collocates.items(), key=itemgetter(1), reverse=True)[:100]
    right_colloc = sorted(right_collocates.items(), key=itemgetter(1), reverse=True)[:100]
    all_colloc = sorted(all_collocates.items(), key=itemgetter(1), reverse=True)[:100]
    return zip(all_colloc, left_colloc, right_colloc)