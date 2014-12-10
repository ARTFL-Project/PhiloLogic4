#!/usr/bin/env python

import sys
sys.path.append('..')
import functions as f
from reports.concordance import fetch_concordance
import os
import re
import unicodedata
from philologic.DB import DB
from concordance import citation_links, concordance_citation, fetch_concordance

from functions.wsgi_handler import WSGIHandler
from bibliography import fetch_bibliography as bibliography
from collocation import tokenize, filter
from functions.ObjectFormatter import adjust_bytes, convert_entities
from functions.FragmentParser import strip_tags
import functions as f

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
    print >> sys.stderr, "BEGIN WORD_PROP_FILTER"
#    db, dbname, path_components, q = wsgi_response(environ,start_response)

    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    config = f.WebConfig()
    
    db = DB(config.db_path + '/data/')    
    request = WSGIHandler(db, environ)
    hits = db.query(request["q"],request["method"],request["arg"],**request.metadata)

    filter_results,pages = filter_words_by_property(hits, config.db_path, request, db, config)
    print >> sys.stderr, "DONE"

    biblio_criteria = []
    for k,v in request.metadata.iteritems():
        if v:
            if k in config.metadata_aliases:
                k = config.metadata_aliases[k]
            biblio_criteria.append('<span class="biblio_criteria">%s: <b>%s</b></span>' % (k.title(), v.decode('utf-8', 'ignore'), ))
    biblio_criteria = ' '.join(biblio_criteria)

#    resource = f.webResources("word_property_filter", debug=db.locals["debug"])
    return f.render_template(concordance=filter_results,pages=pages,query_string=request.query_string,config=config,report="word_property_filter",
                             biblio_criteria=biblio_criteria, template_name="word_property_filter.mako")
"""
    return f.render_template(results=filter_results,db=db,dbname=dbname,q=q,colloc_concordance=colloc_concordance,
                           f=f,path=path, results_per_page=q['results_per_page'], config=config,report="word_property_filter",
                           biblio_criteria=biblio_criteria, template_name="concordance_from_collocation.mako",
                           css= resource.css, js=resource.js)
"""
"""
    wsgi_response(environ, start_response)
    db, path_components, q = parse_cgi(environ)
    dbname = os.path.basename(environ["SCRIPT_FILENAME"].replace("/dispatcher.py",""))
    path = os.getcwd().replace('functions/', '')
    config = f.WebConfig()
    if q['q'] == '':
        return bibliography(f,path, db, dbname,q,environ)
    else:
        hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
        print >> sys.stderr, "FILTERING"
        filter_results = filter_words_by_property(hits, path, q, db, config)
        print >> sys.stderr, "DONE"
        biblio_criteria = []
        for k,v in q["metadata"].iteritems():
            if v:
                if k in config.metadata_aliases:
                    k = config.metadata_aliases[k]
                biblio_criteria.append('<span class="biblio_criteria">%s: <b>%s</b></span>' % (k.title(), v.decode('utf-8', 'ignore'), ))
        biblio_criteria = ' '.join(biblio_criteria)

        resource = f.webResources("word_property_filter", debug=db.locals["debug"])
        return render_template(results=filter_results,db=db,dbname=dbname,q=q,colloc_concordance=colloc_concordance,
                               f=f,path=path, results_per_page=q['results_per_page'], config=config,report="word_property_filter",
                               biblio_criteria=biblio_criteria, template_name="concordance_from_collocation.mako",
                               css= resource.css, js=resource.js)
"""
        
def filter_words_by_property(hits, path, q, db, config, word_filter=True, filter_num=100, stopwords=True):
    concordance_object = {"query": dict([i for i in q])}

    length = config['concordance_length']

    # Do these need to be captured in wsgi_handler?
    word_property = q["word_property"]
    word_property_value = q["word_property_value"]
    word_property_total = q["word_property_total"]
    more_pages = False
    
    new_hitlist = []
    results = []
    for hit in hits:
        ## get my chunk of text ##
        hit_val = get_word_attrib(hit,word_property,db)
        if hit_val == word_property_value:
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

        print >> sys.stderr, "FILTER_COUNT", len(new_hitlist), "vs", (q.start + q.results_per_page)
        if len(new_hitlist) == (q.start + q.results_per_page - 1 ):
            more_pages = True
            break
    
    concordance_object['results'] = results[(q.start - 1):]
    concordance_object["query_done"] = hits.done
    concordance_object['results_length'] = len(hits)
        
    start, end, n = f.link.page_interval(q.results_per_page, hits, q.start, q.end)
    start = q.start
    end = start + q.results_per_page + 1
    if more_pages and end > len(results):
        end = len(results)
    if not more_pages:
        end = len(results)
        word_property_total = end
    else:
        word_property_total = end + 1
    
    concordance_object["description"] = {"start": start, "end": end, "results_per_page": q.results_per_page}
    
    ## Create new hitlist so we can get paging
    h = word_property_hitlist(new_hitlist[q.start:q.start+q.results_per_page])
#    pages = f.link.generate_page_links(q.start, q.results_per_page, q, h)
    pages = f.link.page_links(config,q,int(word_property_total))
    last_page,last_page_link = pages["page_links"][-1]
    if last_page == "Last" and more_pages:
        pages["page_links"][-1] = ("More",last_page_link)
   
    print >> sys.stderr, "PAGES", repr(pages)
    return concordance_object, pages

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
        
