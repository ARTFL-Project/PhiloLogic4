#!/usr/bin/env python
import cgi
import cgitb
import sys
import tempfile
from wsgiref.handlers import CGIHandler
from wsgiref.util import shift_path_info
from wsgiref.util import request_uri
import urlparse
import re
import time
import struct
import urllib
from philo_helpers import *

from philologic import *
from philologic.SqlToms import SqlToms
from philologic.PhiloDB import PhiloDB

def format_stream(text,start,offsets):
    byte_offsets = offsets[:]
    need_l_trim = re.search("^[^<]*?>",text)
    if need_l_trim:
        l_trim_off = need_l_trim.end(0)
        text = text[l_trim_off:]
    else:
        l_trim_off = 0
        
    need_r_trim = re.search("<[^>]*?$",text)
    if need_r_trim:
        r_trim_off = need_r_trim.start(0)
        text = text[:r_trim_off]
    else:
        r_trim_off = 0
        
    start_point = start + l_trim_off
    stream = shlax.parsestring(text)
    output = ""
    for node in stream:        
        if node.type == "text":
            while byte_offsets and node.start + start_point + len(node.content) > byte_offsets[0]:
                word_start = byte_offsets[0] - (node.start + start_point)
                output += node.content[:word_start]
                output += "<span class='hilite'>"
                rest = node.content[word_start:]
                word_end = re.search("[\s\.,;?!'\"]|$",rest).start(0)
                output += rest[:word_end]
                output += "</span>"
                byte_offsets.pop(0)
                node.content = rest[word_end:]
                node.start = node.start + word_start + word_end
            output += node.content            
        if node.type == "StartTag" and (node.name == "l" or node.name == "speaker" or node.name == "ab"):
            output += "<br/>"
        elif node.type == "StartTag" and node.name == "p":
            output += "<p/>"

    return output
        
def transform(node):
    if node.attrib.get("class","") != "hilite" and node.attrib.get("class","") != "context": 
        node.tag = None
    if node.text: node.text = re.sub(r"\s+", " ",node.text).decode("utf-8","ignore") # ignore leading/trailing malformed chars.
    if node.tail: node.tail = re.sub(r"\s+", " ",node.tail).decode("utf-8","ignore")
    for child in node:
        transform(child)

def conc_service(environ, start_response):
    status = '200 OK' # HTTP Status
    headers = [('Content-type', 'text/html; charset=UTF-8')] # HTTP Headers
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
    q_start = int(environ["parsed_params"].get('q_start',[0])[0]) or 1 # better checking.  this doesn't catch 0...which helps for now.
    q_end = int(environ["parsed_params"].get('q_end',[0])[0]) or q_start + 49 # fine.  python lists are exclusive at the end.
    width = int(environ["parsed_params"].get("width",[0])[0]) or 400
    status = "running query for %s @ %s with arg %s" % (qs,dbname,query_arg)
    
    metadata_fields = db.locals["metadata_fields"]
    query_metadata = {}
    
    for meta_f in metadata_fields:
        if meta_f in environ["parsed_params"]:
            query_metadata[meta_f] = environ["parsed_params"][meta_f][0]    

    content = ""
    q = db.query(qs,query_method,query_arg,**query_metadata)
    
    while not q.done:
        time.sleep(.05)
        q.update()

    l = len(q)
    if q_end > l:
        q_end = l
    status += ".  displaying %d - %d of %d hits." % (q_start,q_end,l)
        
    yield("<html>")
    yield("<head>")
    yield("<title>%s: search for %s</title>" % (dbname, qs))
    #opensearch metadata in meta tags here.
    #total length, start index, hits per page.
    yield("</head>")
    yield("<body>")
    yield("<div class='philologic_concordance'>")
    yield("<p class='description'>%s</p>" % status)
    if l > 0:
        yield "<ol start='%d'>" % q_start
        for hit in q[q_start-1:q_end]:
            doc_id = q.get_doc(hit)
            offsets = q.get_bytes(hit)
            offsets.sort()
            first_offset = offsets[0]
            doc = db.toms[doc_id]
            div1 = db.toms[hit[:2]]
            div2 = db.toms[hit[:3]]
            filename = doc["filename"]

            url = hit_to_link(db,hit)

            yield "<li class='philologic_occurence'>\n"

            yield db.locals["make_cite"](db,hit,url)

            yield("</a>\n")

            conc_start = first_offset - width
            if conc_start < 0: conc_start = 0
            text_path = dbpath + "/TEXT/" + filename
            text_file = open(text_path)
            text_file.seek(conc_start)
            text = text_file.read(width * 2)
            context = format_stream(text,conc_start,offsets)
            yield(context)

            yield("</li>\n")
        yield("</ol>")
        pages = l / 50 + 1
        more = ""

        yield("<div class='more'>")
        prev_off = 1
        next_off = min(prev_off + 49,l)
        p_count = 0

        while True:
            new_uri = make_link(qs,query_method,query_arg,start=prev_off,end=next_off,**query_metadata)
            yield "<a href='%s'>%d-%d</a> " % (new_uri,prev_off,next_off)
            if prev_off < q_start:
                yield "... "
                prev_off = q_start + 50
            else:
                prev_off += 50
            next_off = min(prev_off + 49,l)
            p_count += 1
            if p_count > 10: break
            if next_off == l: break
        last_page = 50 * (l // 50) + 1
        if prev_off <= last_page:
            if prev_off < last_page:
                yield "... "
            prev_off = last_page
            next_off = l
            new_uri = make_link(qs,query_method,query_arg,start=prev_off,end=next_off,**query_metadata)
            yield "<a href='%s'>%d-%d</a> " % (new_uri,prev_off,next_off)
        yield("</div>")
    yield("</div>")
    yield("</body>")
    yield("</html>")
    
    
if __name__ == "__main__":
    CGIHandler().run(conc_service)
