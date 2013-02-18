#!/usr/bin/env python

import sys
sys.path.append('..')
import functions as f
import os
import re
from functions.wsgi_handler import wsgi_response
from bibliography import bibliography
from render_template import render_template
from collocation import tokenize, filter
from functions.format import adjust_bytes, clean_text, chunkifier

def concordance_from_collocation(environ,start_response):
    db, dbname, path_components, q = wsgi_response(environ,start_response)
    path = os.getcwd().replace('functions/', '')
    if q['q'] == '':
        return bibliography(f,path, db, dbname,q,environ)
    else:
        hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
        return render_template(results=hits,db=db,dbname=dbname,q=q,fetch_colloc_concordance=fetch_colloc_concordance,
                               fetch_concordance=fetch_concordance,f=f,path=path, results_per_page=q['results_per_page'],
                               template_name="concordance_from_collocation.mako")
        
def fetch_colloc_concordance(results, path, q, filter_words=100):
    within_x_words = q['word_num']
    direction = q['direction']
    collocate = q['collocate'].decode('utf-8', 'ignore')
    collocate_num = q['collocate_num']
    
    ## set up filtering of most frequent 100 terms ##
    filter_list_path = path + '/data/frequencies/word_frequencies'
    filter_words_file = open(filter_list_path)

    line_count = 0
    filter_list = set([])

    for line in filter_words_file:
        line_count += 1
        word = line.split()[0]
        filter_list.add(word.decode('utf-8', 'ignore'))
        if line_count > filter_words:
                break
    
    new_hitlist = []
    for hit in results:
        ## get my chunk of text ##
        bytes, byte_start = adjust_bytes(hit.bytes, 400)
        conc_text = f.get_text(hit, byte_start, 400, path)
        conc_left, conc_middle, conc_right = chunkifier(conc_text, bytes)
        if direction =='left':
            words = tokenize(conc_left, filter_list, within_x_words, direction)
        elif direction == 'right':
            words = tokenize(conc_right, filter_list, within_x_words, direction)
        else:
            words = tokenize(conc_left, filter_list, within_x_words, 'left')
            words.extend(tokenize(conc_right, filter_list, within_x_words, 'right'))
        if collocate in set(words):
            count = words.count(collocate)
            hit.collocate_num = count
            new_hitlist.append(hit)

        if len(new_hitlist) > (q["start"] + q["results_per_page"]):
            break
            
    
    return collocation_hitlist(new_hitlist, collocate_num)

def fetch_concordance(hit, path, q, length=2000):
    bytes, byte_start = f.format.adjust_bytes(hit.bytes, length)
    conc_text = f.get_text(hit, byte_start, length, path)
    conc_start, conc_middle, conc_end = f.format.chunkifier(conc_text, bytes, highlight=True)
    conc_start = f.format.clean_text(conc_start)
    conc_end = f.format.clean_text(conc_end)
    conc_text = conc_start + conc_middle + conc_end
    conc_text = conc_text.decode('utf-8', 'ignore')
    highlight_index = conc_text.find('<span class="highlight"')
    begin = highlight_index - 200 ## make sure the highlighted term does not get hidden
    end = highlight_index + 200
    first_span = '<span class="begin_concordance" style="display:none;">'
    second_span = '<span class="end_concordance" style="display:none;">'
    conc_text =  first_span + conc_text[:begin] + '</span>' + conc_text[begin:end] + second_span + conc_text[end:] + '</span>'
    split_text = re.split(r"([^ \.,;:?!\"\n\r\t\(\)]+)|([\.;:?!])", conc_text)
    keep_text = []
    for w in split_text:
        if w:
            if w.lower() == q['collocate'].decode('utf-8', 'ignore'):
                w = '<span class="collocate">%s</span>' % w
            keep_text.append(w)
    conc_text = ''.join(keep_text)
    return conc_text  
    
class collocation_hitlist(object):
    
    def __init__(self, hitlist, collocate_num):
        self.done = True
        self.num = collocate_num
        self.hitlist = hitlist
        
    def __getitem__(self, key):
        return self.hitlist[key]
        
    def __getattr__(self, name):
        return self.hitlist[name]
        
    def __len__(self):
        return len(self.hitlist)
        