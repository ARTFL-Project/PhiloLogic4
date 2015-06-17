#!/usr/bin/env python

import sys
sys.path.append('..')
import functions as f
from reports.concordance import fetch_concordance
import os
import re
import unicodedata
from philologic.DB import DB
from wsgiref.handlers import CGIHandler
from concordance import citation_links, concordance_citation, fetch_concordance
from functions.wsgi_handler import WSGIHandler
from functions.ObjectFormatter import adjust_bytes, convert_entities
from functions.FragmentParser import strip_tags
try:
    import simplejson as json
except ImportError:
    print >> sys.stderr, "Please install simplejson for better performance"
    import json


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

def word_property_filter(environ,start_response):
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response('200 OK',headers)
    
    hits = db.query(request["q"],request["method"],request["arg"],**request.metadata)
    filter_results = filter_words_by_property(hits, config.db_path, request, db, config)
    yield json.dumps(filter_results)
  
def filter_words_by_property(hits, path, q, db, config, word_filter=True, filter_num=100, stopwords=True):
    concordance_object = {"query": dict([i for i in q])}

    length = config['concordance_length']

    # Do these need to be captured in wsgi_handler?
    word_property = q["word_property"]
    word_property_value = q["word_property_value"]
    word_property_total = q["word_property_total"]
    
    new_hitlist = []
    results = []
    position = 0
    more_pages = False
    
    if q.start == 0:
        start = 1
    else:
        start = q.start

    for hit in hits:
        ## get my chunk of text ##
        hit_val = get_word_attrib(hit,word_property,db)

        if hit_val == word_property_value:
            position += 1
            if position < start:
                continue
            new_hitlist.append(hit)
            citation_hrefs = citation_links(db, config, hit)
            metadata_fields = {}
            for metadata in db.locals['metadata_fields']:
                metadata_fields[metadata] = hit[metadata]
            citation = concordance_citation(hit, citation_hrefs)
            context = fetch_concordance(db, hit, config.db_path, config.concordance_length)
            result_obj = {"philo_id": hit.philo_id, "citation": citation, "citation_links": citation_hrefs, "context": context,
                          "metadata_fields": metadata_fields, "bytes": hit.bytes, "collocate_count": 1}            
            results.append(result_obj)

        if len(new_hitlist) == (q.results_per_page):
            more_pages = True
            break
    
    end = start + len(results) - 1 
    if len(results) < q.results_per_page:
        word_property_total = end
    else:
        word_property_total = end + 1
    concordance_object['results'] = results
    concordance_object["query_done"] = hits.done
    concordance_object['results_length'] = word_property_total
    concordance_object["description"] = {"start": start, "end": end, "results_per_page": q.results_per_page, "more_pages": more_pages}    
    print >> sys.stderr, "DONE"
    return concordance_object

def get_word_ids(hit):
    philo_id = hit.philo_id[:]
    parent_id = philo_id[:6] 
    remaining = list(philo_id[7:])
    results = []
    bytes = []
    while remaining:
        results += [ parent_id + (remaining.pop(0),) ]
        if remaining:
            results[-1] += ( remaining.pop(0), )    
    results.sort(key=lambda x:x[-1])
    return [r[:7] for r in results]
    
def get_word_attrib(n,field,db):
    print >> sys.stderr, "HIT", repr(n.philo_id)
    words = n.words
    print >> sys.stderr, "WORDS", repr(words)
    key = field
    if key == "token":
        key = "philo_name"
    if key == "morph":
        key = "pos"
    print >> sys.stderr, "looking up %s" % key
    val = ""
    for word in words:
        word_obj = word
        if val:
            val += "_"
        if word_obj[key]:
            val += word_obj[key]
        else:
            val += "NULL"
        print >> sys.stderr, "ROW", repr(word_obj.row)

    if isinstance(val,unicode):
        return val.encode("utf-8")
    return val

class word_property_hitlist(object):
    
    def __init__(self, hitlist):
        self.done = True
        self.hitlist = hitlist
        
    def __getitem__(self, key):
        return self.hitlist[key]
        
    def __getattr__(self, name):
        return self.hitlist[name]
        
    def __len__(self):
        return len(self.hitlist)
        

if __name__ == "__main__":
    CGIHandler().run(word_property_filter)

