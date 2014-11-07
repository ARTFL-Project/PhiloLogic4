#!/usr/bin/env python

import sys
sys.path.append('..')
import functions as f
import reports as r
import os
import re
from functions.wsgi_handler import wsgi_response
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
        return r.fetch_bibliography(f,path, db, dbname,q,environ)
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
    pages = f.link.generate_page_links(concordance_object['description']['start'], q['results_per_page'], q, hits)
    return render_template(concordance=concordance_object, q=concordance_object["query"], db=db,dbname=dbname,path=path,
                           biblio_criteria=biblio_criteria,config=config, template_name="concordance.mako", report="concordance",
                           pages=pages, css=resource.css, js=resource.js)

def concordance_results(db, q, config, path):
    hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
    start, end, n = f.link.page_interval(q['results_per_page'], hits, q["start"], q["end"])
    concordance_object = {"description": {"start": start, "end": end, "results_per_page": q['results_per_page']},
                          "query": q}
    results = []
    for hit in hits[start - 1:end]:
        citation_hrefs = f.citation_links(db, config, hit)
        metadata_fields = {}
        for metadata in db.locals['metadata_fields']:
            metadata_fields[metadata] = hit[metadata]
        citation = concordance_citation(hit, citation_hrefs, metadata_fields)
        context = fetch_concordance(hit, path, config.concordance_length)
        result_obj = {"philo_id": hit.philo_id, "citation": citation, "citation_links": citation_hrefs, "context": context,
                      "metadata_fields": metadata_fields, "bytes": hit.bytes}
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

def concordance_citation(hit, citation_hrefs, metadata_fields):
    """ Returns a representation of a PhiloLogic object and all its ancestors
        suitable for a precise concordance citation. """
    
    ## Doc level metadata
    title = '<a href="%s">%s</a>' % (citation_hrefs['doc'], hit.doc.title.strip())
    author = hit.doc.author
    if author:
        citation = "%s <i>%s</i>" % (author.strip(),title)
    else:
        citation = "<i>%s</i>" % title
    date = hit.doc.date
    if date:
        try:
            citation += " [%s]" % str(date)
        except:
            pass
    
    ## Div level metadata
    div1_name = hit.div1.head
    if not div1_name:
        if hit.div1.philo_name == "__philo_virtual":
            div1_name = "Section"
        else:
            div1_name = hit.div1.philo_name
    div2_name = hit.div2.head
    div3_name = hit.div3.head
    
    if div1_name:
        citation += u"<a href='%s'>%s</a>" % (citation_hrefs['div1'],div1_name.strip())
    if div2_name:
        citation += u"<a href='%s'>%s</a>" % (citation_hrefs['div2'],div2_name.strip())
    if div3_name:
        citation += u"<a href='%s'>%s</a>" % (citation_hrefs['div3'],div3_name.strip())
        
    ## Paragraph level metadata
    if "para" in citation_hrefs:
        citation += "<a href='%s'>%s</a>" % (citation_hrefs['para'], hit.para.who)
    
    page_obj = hit.page
    if page_obj['n']:
        page_n = page_obj['n']
        citation += u" [page %s] " % page_n    
    citation = u'<span class="philologic_cite">' + citation + "</span>"
    return citation