#!/usr/bin/env python 
import sys
import re
import time
from philologic.PhiloDB import PhiloDB
import philologic.shlaxtree as st
import elementtree.ElementTree as et
from wsgiref.handlers import CGIHandler
from wsgiref.util import shift_path_info
import urlparse
import json
from philo_helpers import *

def colloc_json_service(environ,start_response):
    status = '200 OK' # HTTP Status
    headers = [('Content-type', 'application/json; charset=UTF-8')] # HTTP Headers
    start_response(status, headers)
    environ["parsed_params"] = urlparse.parse_qs(environ["QUERY_STRING"],keep_blank_values=True)
    # a wsgi app is supposed to return an iterable;
    # yielding lets you stream, rather than generate everything at once.
    if "philologic_dbname" in environ:
        dbname = environ["philologic_dbname"]
    else:
        dbname = environ["parsed_params"]["philologic_dbname"][0]
    myname = environ["SCRIPT_NAME"]
    dbpath = "/var/lib/philologic/databases/" + dbname
    db = PhiloDB(dbpath,7)
    obj = []
    count = 0
    corpus_file = None
    corpus_size = 7
    corpus_count = 0
    
    qs = environ["parsed_params"]["query"][0]
    query_method = environ["parsed_params"].get("query_method",[0])[0] or None
    query_arg = environ["parsed_params"].get("query_arg",[0])[0] or 0

    q_start = int(environ["parsed_params"].get('q_start',[0])[0]) or 1
    q_end = int(environ["parsed_params"].get('q_end',[0])[0]) or q_start + 499  
    width = int(environ["parsed_params"].get("width",[0])[0]) or 100
    status = "running query for %s @ %s: " % (qs,dbname)

    metadata_fields = ["author","title","date"]
    query_metadata = {}
    
    for meta_f in metadata_fields:
        if meta_f in environ["parsed_params"]:
            query_metadata[meta_f] = environ["parsed_params"][meta_f][0]    

    print >> sys.stderr, query_metadata
    content = ""
    q = db.query(qs,query_method,query_arg,**query_metadata)
    
    while len(q) <= q_end and not q.done:
        time.sleep(.05)
        q.update()

    l = len(q)
    if q_end > l:
        q_end = l
    print >> sys.stderr, "%d total hits. aggregating." % (l)

    last_doc = -1
    collocates = {}
    text_file = None
    if l > 0:
        for hit in q[q_start - 1:q_end]:
            doc_id = q.get_doc(hit)
            offsets = q.get_bytes(hit)
            offsets.reverse()
            first_offset = offsets[0]

            conc_start = first_offset - 100
            if conc_start < 0: conc_start = 0
                        
            if doc_id > last_doc:
                filename = db.toms[doc_id]["filename"]
                last_doc = doc_id
                text_path = dbpath + "/TEXT/" + filename
                text_file = open(text_path)                       

            text_file.seek(conc_start)
            text = text_file.read(width * 2)

            
            #trim the text
            need_l_trim = re.search("^[^<]*>",text)
            if need_l_trim:
                l_trim_off = need_l_trim.end(0)
                text = text[l_trim_off:]
            else:
                l_trim_off = 0
                
            need_r_trim = re.search("<[^>]*$",text)
            if need_r_trim:
                r_trim_off = need_r_trim.start(0)
                text = text[:r_trim_off]
            else:
                r_trim_off = 0
            
            conc_start += l_trim_off
            for token in list(re.finditer(r"(<[^>]+>)|(\w+)",text))[1:-1]:
                if token.group(2):
                    t_off = token.start(2) + conc_start
                    if t_off not in offsets:
                        t_type = token.group(2)
                        if t_type in collocates:
                            collocates[t_type] += 1
                        else:
                            collocates[t_type] = 1

        results = []
        total_words = 0
        page_width = q_end - q_start + 1
        for n,f in sorted(collocates.items(),key=lambda x:x[1],reverse=True):
            if f > 5: # UGLY!!!
                filter_metadata = dict(query_metadata.items())
                filter_metadata["colloc_filter"] = n
                url = make_link(qs,query_method,query_arg,**filter_metadata)
                results.append({"label":n,"count":f,"url":url,"rate":float(f)/l})
                total_words += f
    pages = []
    page_width = q_end - q_start + 1
    for p_start in range(q_end + 1,l,page_width):
        page_metadata = dict(query_metadata.items())
        page_metadata["field"] = "collocates"
        page_metadata["format"] = "json"
        page_metadata["report"] = "frequency"
        
        p_end = min(l,p_start + page_width - 1)
        p_url = make_link(qs,query_method,query_arg,start=p_start,end=p_end,**page_metadata)
        pages.append(p_url)
    wrapper = {"result":results,"remaining_pages":pages,"length":l,"q_start":q_start,"q_end":q_end,"total_words":total_words,"field":"word"}
    yield json.dumps(wrapper,indent=1)

if __name__ == "__main__":
    CGIHandler().run(colloc_service)
