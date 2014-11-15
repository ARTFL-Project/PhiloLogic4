#!/usr/bin/env python

import sys
sys.path.append('..')
import functions as f
import reports as r
import os
import re
from functions.wsgi_handler import wsgi_response, parse_cgi
from functions.ObjectFormatter import convert_entities, adjust_bytes, valid_html_tags, xml_to_html_class
from functions.FragmentParser import parse
from lxml import etree
import json

strip_start_punctuation = re.compile("^[,?;.:!']")
begin_match = re.compile(r'^[^<]*?>')
start_cutoff_match = re.compile(r'^[^ <]+')
end_match = re.compile(r'<[^>]*?\Z')
space_match = re.compile(r" ?([-'])+ ")

def concordance(environ,start_response):
    wsgi_response(environ, start_response)
    db, path_components, q = parse_cgi(environ)
    dbname = os.path.basename(environ["SCRIPT_FILENAME"].replace("/dispatcher.py",""))
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
    biblio_criteria = f.biblio_criteria(concordance_object['query'], config)
    pages = f.link.generate_page_links(concordance_object['description']['start'], q['results_per_page'], q, hits)
    return f.render_template(concordance=concordance_object, q=concordance_object["query"], db=db,dbname=dbname,
                           biblio_criteria=biblio_criteria,config=config, template_name="concordance.mako", report="concordance",
                           pages=pages)

def concordance_results(db, q, config, path):
    hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
    start, end, n = f.link.page_interval(q['results_per_page'], hits, q["start"], q["end"])
    concordance_object = {"description": {"start": start, "end": end, "results_per_page": q['results_per_page']},
                          "query": q}
    results = []
    for hit in hits[start - 1:end]:
        citation_hrefs = citation_links(db, config, hit)
        metadata_fields = {}
        for metadata in db.locals['metadata_fields']:
            metadata_fields[metadata] = hit[metadata]
        citation = concordance_citation(hit, citation_hrefs)
        context = fetch_concordance(db, hit, path, config.concordance_length)
        result_obj = {"philo_id": hit.philo_id, "citation": citation, "citation_links": citation_hrefs, "context": context,
                      "metadata_fields": metadata_fields, "bytes": hit.bytes}
        results.append(result_obj)
    concordance_object["results"] = results
    concordance_object['results_len'] = len(hits)
    concordance_object["query_done"] = hits.done
    return concordance_object, hits

def citation_links(db, config, i):
    """ Returns a representation of a PhiloLogic object and all its ancestors
        suitable for a precise concordance citation. """
    doc_href = f.make_absolute_object_link(config,i.philo_id[:1],i.bytes)
    div1_href = f.make_absolute_object_link(config,i.philo_id[:2], i.bytes)
    div2_href = f.make_absolute_object_link(config,i.philo_id[:3], i.bytes)
    div3_href = f.make_absolute_object_link(config,i.philo_id[:4], i.bytes)
    
    links = {"doc": doc_href, "div1": div1_href, "div2": div2_href, "div3": div3_href}
    
    speaker_name = i.para.who
    if speaker_name:
        links['para'] = f.make_absolute_object_link(config, i.philo_id[:5], i.bytes)
    return links

def concordance_citation(hit, citation_hrefs):
    """ Returns a representation of a PhiloLogic object and all its ancestors
        suitable for a precise concordance citation. """
    
    ## Doc level metadata
    title = '<a href="%s">%s</a>' % (citation_hrefs['doc'], hit.title.strip())
    if hit.author:
        citation = "%s <i>%s</i>" % (hit.author.strip(),title)
    else:
        citation = "<i>%s</i>" % title
    if hit.date:
        try:
            citation += " [%s]" % str(hit.date)
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
        try:
            citation += "<a href='%s'>%s</a>" % (citation_hrefs['para'], hit.who)
        except KeyError: ## no who keyword
            pass
    
    page_obj = hit.page
    if page_obj['n']:
        page_n = page_obj['n']
        citation += u" [page %s] " % page_n    
    citation = u'<span class="philologic_cite">' + citation + "</span>"
    return citation

def fetch_concordance(db, hit, path, context_size):
    ## Determine length of text needed
    byte_distance = hit.bytes[-1] - hit.bytes[0]
    length = context_size + byte_distance + context_size
    bytes, byte_start = adjust_bytes(hit.bytes, length)
    conc_text = f.get_text(hit, byte_start, length, path)
    conc_text = format_concordance(conc_text, db.locals['word_regex'], bytes)
    conc_text = convert_entities(conc_text)
    conc_text = strip_start_punctuation.sub("", conc_text)
    return conc_text

def format_concordance(text, word_regex, bytes=[]):
    removed_from_start = 0
    begin = begin_match.search(text)
    if begin:
        removed_from_start = len(begin.group(0))
        text = text[begin.end(0):]
    start_cutoff = start_cutoff_match.search(text)
    if start_cutoff:
        removed_from_start += len(start_cutoff.group(0))
        text = text[start_cutoff.end(0):]
    removed_from_end = 0
    end = end_match.search(text)
    if end:
        removed_from_end = len(end.group(0))
        text = text[:end.start(0)]
    if bytes:
        bytes = [b - removed_from_start for b in bytes]
        new_text = ""
        last_offset = 0
        for b in bytes:
            if b > 0 and b < len(text):
                new_text += text[last_offset:b] + "<philoHighlight/>"
                last_offset = b
        text = new_text + text[last_offset:]
    xml = f.FragmentParser.parse(text)
    length = 0
    allowed_tags = set(['philoHighlight', 'l', 'ab', 'ln', 'w', 'sp', 'speaker', 'stage', 'i', 'sc', 'scx', 'br'])
    text = u''
    for el in xml.iter():
        if el.tag not in allowed_tags:
            el.tag = 'span'
        elif el.tag == "ab" or el.tag == "ln":
            el.tag = "l"
        if "id" in el.attrib:  ## kill ids in order to avoid the risk of having duplicate ids in the HTML
            del el.attrib["id"]
        if el.tag == "sc" or el.tag == "scx":
            el.tag = "span"
            el.attrib["class"] = "small-caps"
        if el.tag == "philoHighlight":        
            word_match = re.match(word_regex, el.tail, re.U)
            if word_match:
                el.text = el.tail[:word_match.end()]
                el.tail = el.tail[word_match.end():]
            el.tag = "span"
            el.attrib["class"] = "highlight"
        if el.tag not in valid_html_tags:
            el = xml_to_html_class(el)
    output = etree.tostring(xml)
    output = re.sub(r'\A<div class="philologic-fragment">', '', output)
    output = re.sub(r'</div>\Z', '', output)
    ## remove spaces around hyphens and apostrophes
    output = space_match.sub('\\1', output)
    return output