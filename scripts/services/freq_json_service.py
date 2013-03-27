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

def freq_json_service(environ,start_response):
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
    metadata_fields = ["author","title","date"]
    query_metadata = {}
    
    qs = environ["parsed_params"]["query"][0]
    query_method = environ["parsed_params"].get("query_method",[0])[0] or None
    query_arg = environ["parsed_params"].get("query_arg",[0])[0] or 0

    q_start = int(environ["parsed_params"].get('q_start',[0])[0]) or 1
    q_end = int(environ["parsed_params"].get('q_end',[0])[0]) or q_start + 1999 
    width = int(environ["parsed_params"].get("width",[0])[0]) or 100
    
    for meta_f in metadata_fields:
        if meta_f in environ["parsed_params"]:
            query_metadata[meta_f] = environ["parsed_params"][meta_f][0]
    
    field = environ["parsed_params"].get("field",[""])[0] or "author"
    #need a field param.  author default?
    status = "running query for %s @ %s: " % (qs,dbname)

    content = ""
    q = db.query(qs,query_method,query_arg,**query_metadata)
    
    while len(q) <= q_end and not q.done:
        time.sleep(.05)
        q.update()

    l = len(q)
    if q_end > l:
        q_end = l
    status += "%d total hits. aggregating." % (l)

    last_doc = -1
    authors = {}
    titles = {}
    counts = {}
    totalcounts = {}
    decades = {}
    #opensearch metadata in meta tags here.
    #total length, start index, hits per page.
    if l > 0:
        for hit in q[q_start - 1:q_end]: #need to page q
            byte_offset = hit[6]
            offsets = list(hit[6:])
            offsets.reverse()
            doc_id = hit[0]
            if doc_id > last_doc:
                metadata = db.toms[doc_id]
            
            label = metadata[field]
            if field == "date":
                date = label
                label = "%s0 - %s9" % (date[:-1], date[:-1])
                decades[label] = date[:-1] + "%"
            counts[label] = counts.get(label,0) + 1
            if doc_id != last_doc:
                count = metadata["word_count"]
        
        result = []

        filter_metadata = dict(query_metadata.items()) 
        for n,f in sorted(counts.items(),key=lambda x:x[1], reverse=True):
            if field == "date":
                total = sum(int(ob["word_count"]) for ob in db.toms.dbh.execute("select word_count from toms where date like '%s';" % decades[n]))
                filter_metadata[field] = decades[n]
            else:
                total = sum(int(ob["word_count"]) for ob in db.toms.dbh.execute("select word_count from toms where %s=?;" % field,(n,)))                        
                filter_metadata[field] = n
            rate = float(f) / total
            url = make_link(qs,query_method,query_arg,**filter_metadata)
            result.append( {"label":n,"count":f,"total_count":total,"rate":rate,"url":url})

    pages = []
    page_width = q_end - q_start + 1
    page_metadata = dict(query_metadata.items())
    page_metadata["report"] = "frequency"
    page_metadata["field"] = field
    for p_start in range(q_end + 1,l,page_width):
        p_end = min(l,p_start + page_width - 1)
        p_url = make_link(qs,query_method,query_arg,start=p_start,end=p_end,**page_metadata)
        pages.append(p_url)

    wrapper = {"length":l,"remaining_pages":pages,"result":result,"q_start":q_start,"q_end":q_end,"field":field}
    yield(json.dumps(wrapper,indent=1))


if __name__ == "__main__":
    CGIHandler().run(freq_service)
