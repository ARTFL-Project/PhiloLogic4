#!/usr/bin/env python

import sys
sys.path.append('..')
import functions as f
import os
import re
from functions.wsgi_handler import wsgi_response
from bibliography import fetch_bibliography as bibliography
from render_template import render_template
from functions.ObjectFormatter import format_concordance, convert_entities, adjust_bytes
from functions.FragmentParser import parse
import json

strip_start_punctuation = re.compile("^[,?;.:!']")

def concordance(environ,start_response):
    db, dbname, path_components, q = wsgi_response(environ,start_response)
    path = os.getcwd().replace('functions/', '')
    config = f.WebConfig()
    if q['q'] == '':
        return bibliography(f,path, db, dbname,q,environ)
    else:
        concordance_object, hits = concordance_results(db, q, config, path)
        if q['format'] == "json":
            # Remove db_path from query object since we don't want to expose that info to the client
            del concordance_object['query']['dbpath']
            return json.dumps(concordance_object)
        return render_concordance(concordance_object, hits, q, db, dbname, path, config)
        
def render_concordance(concordance_object, hits, q, db, dbname, path, config):
    resource = f.webResources("concordance", debug=db.locals["debug"])
    biblio_criteria = f.biblio_criteria(concordance_object['query'], config)
    pages = generate_page_links(concordance_object['description']['start'], q['results_per_page'], q, hits)
    return render_template(concordance=concordance_object, q=concordance_object["query"], db=db,dbname=dbname,path=path,
                           biblio_criteria=biblio_criteria,config=config, template_name="concordance.mako", report="concordance",
                           pages=pages, css=resource.css, js=resource.js)

def concordance_results(db, q, config, path):
    hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
    start, end, n = f.link.page_interval(q['results_per_page'], hits, q["start"], q["end"])
    concordance_object = {"description": {"start": start, "end": end, "n": n, "results_per_page": q['results_per_page']},
                          "query": q}
    results = []
    for hit in hits[start - 1:end]:
        citation = f.concordance_citation(db, config, hit)
        context = fetch_concordance(hit, path, config.concordance_length)
        result_obj = {"philo_id": hit.philo_id, "citation": citation, "context": context, "bytes": hit.bytes}
        results.append(result_obj)
    concordance_object["results"] = results
    concordance_object['results_len'] = len(hits)
    concordance_object["query_done"] = hits.done
    return concordance_object, hits


def fetch_concordance(hit, path, context_size):
    ## Determine length of text needed
    byte_distance = hit.bytes[-1] - hit.bytes[0]
    length = context_size + byte_distance + context_size
    bytes, byte_start = adjust_bytes(hit.bytes, length)
    conc_text = f.get_text(hit, byte_start, length, path)
    conc_text = format_concordance(conc_text, bytes)
    conc_text = convert_entities(conc_text)
    conc_text = strip_start_punctuation.sub("", conc_text)
    return conc_text

def generate_page_links(start, results_per_page, q, results):
    current_page, my_pages, page_num = f.link.pager(start, results_per_page, q, results)
    if results.done and page_num != my_pages[-1][0]:
        last_page = f.link.find_page_number(len(results), results_per_page)
        last_page_link = f.link.page_linker(last_page, results_per_page, q)
    else:
        last_page_link = None
    pages = {"current_page": current_page, "my_pages": my_pages, "page_num": page_num, "last_page_link": last_page_link}
    return pages
