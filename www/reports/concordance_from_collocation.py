#!/usr/bin/env python

import sys
sys.path.append('..')
import functions as f
import os
import re
import unicodedata
from philologic.DB import DB
from functions.wsgi_handler import WSGIHandler
from bibliography import fetch_bibliography as bibliography
from collocation import tokenize, filter, build_filter_list, split_concordance
from concordance import citation_links, concordance_citation, fetch_concordance
from functions.ObjectFormatter import adjust_bytes, convert_entities
from functions.FragmentParser import strip_tags


end_highlight_match = re.compile(r'.*<span class="highlight">[^<]*?(</span>)')
token_regex = re.compile(r'(\W)', re.U)

left_truncate = re.compile (r"^\w+", re.U)
right_truncate = re.compile("\w+$", re.U)
word_identifier = re.compile("\w", re.U)
highlight_match = re.compile(r'<span class="highlight">[^<]*?</span>')
#token_regex = re.compile(r'[\W\d]+', re.U)

begin_match = re.compile(r'^[^<]*?>')
start_cutoff_match = re.compile(r'^[^ <]+')
end_match = re.compile(r'<[^>]*?\Z')
no_tag = re.compile(r'<[^>]+>')

def concordance_from_collocation(environ,start_response):
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    if request.no_q:
        return r.fetch_bibliography(db, request, config, start_response)
    else:
        headers = [('Content-type', 'text/html; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
        start_response('200 OK',headers)
        hits = db.query(request["q"],request["method"],request["arg"],**request.metadata)
        concordance_object, pages = fetch_colloc_concordance(hits, request, db, config)
        biblio_criteria = f.biblio_criteria(request, config)
        return f.render_template(concordance=concordance_object,pages=pages,query_string=request.query_string,config=config,report="concordance_from_collocation",
                                 biblio_criteria=biblio_criteria, template_name="concordance_from_collocation.mako")
        
def fetch_colloc_concordance(hits, q, db, config, word_filter=True, filter_num=100, stopwords=True):
    concordance_object = {"query": dict([i for i in q])}
    
    length = config['concordance_length']
    within_x_words = int(q['word_num'])
    direction = q['direction']
    collocate = unicodedata.normalize('NFC', q['collocate'].decode('utf-8', 'ignore'))
    collocate_num = int(q['collocate_num'])
    
    filter_list = build_filter_list(q, config)
    
    results = []
    colloc_hitlist = []
    position = 0
    for hit in hits:
        conc_left, conc_right = split_concordance(hit, length, config.db_path)
        
        if direction =='left':
            words = tokenize(conc_left, filter_list, within_x_words, direction, db)
        elif direction == 'right':
            words = tokenize(conc_right, filter_list, within_x_words, direction, db)
        else:
            words = tokenize(conc_left, filter_list, within_x_words, 'left', db)
            words.extend(tokenize(conc_right, filter_list, within_x_words, 'right', db))
        if collocate in set(words):
            position += 1
            if position < q.start: ## Make sure we start appending hits at the right position in the hitlist
                continue
            count = words.count(collocate)
            hit.colloc_num = count
            colloc_hitlist.append(hit)
            citation_hrefs = citation_links(db, config, hit)
            metadata_fields = {}
            for metadata in db.locals['metadata_fields']:
                metadata_fields[metadata] = hit[metadata]
            citation = concordance_citation(hit, citation_hrefs)
            context = colloc_concordance(db, hit, config.db_path, q, config.concordance_length)
            result_obj = {"philo_id": hit.philo_id, "citation": citation, "citation_links": citation_hrefs, "context": context,
                          "metadata_fields": metadata_fields, "bytes": hit.bytes, "collocate_count": count}
            results.append(result_obj)

        if len(results) == (q.results_per_page):
            break
    
    concordance_object['results'] = results
    concordance_object["query_done"] = hits.done
    concordance_object['results_length'] = len(hits)
    
    start, end, n = f.link.page_interval(q.results_per_page, hits, q.start, q.end)
    if end > len(results) + start - 1:
        end = len(results) + start - 1
    concordance_object["description"] = {"start": start, "end": end, "results_per_page": q.results_per_page}
    
    ## Create new hitlist so we can get paging
    colloc_hitlist = collocation_hitlist(colloc_hitlist, collocate_num)
    pages = f.link.generate_page_links(concordance_object['description']['start'], q.results_per_page, q, colloc_hitlist)
    
    return concordance_object, pages

def colloc_concordance(db, hit, path, q, context_size):
    conc_text = fetch_concordance(db, hit, path, context_size)
    collocate = q['collocate'].decode('utf-8', 'ignore')
    collocate_match = re.compile(r'(?<!<span class="highlight">)(%s)(.*?)' % collocate, flags=re.U|re.I)
    conc_text = collocate_match.sub(r'<span class="collocate">\1\2</span>', conc_text)
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
        return int(self.num)
        