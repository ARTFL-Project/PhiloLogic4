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

def colloc_service(environ,start_response):
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
    q_start = int(environ["parsed_params"].get('q_start',[0])[0]) or 0
    q_end = int(environ["parsed_params"].get('q_end',[0])[0]) or q_start + 50  
    width = int(environ["parsed_params"].get("width",[0])[0]) or 100
    q_title = environ["parsed_params"].get("title",[""])[0] or ""
    q_author = environ["parsed_params"].get("author",[""])[0] or ""
    status = "running query for %s @ %s: " % (qs,dbname)

    metadata = {}
    if q_author:
        metadata["author"] = q_author
    if q_title:
        metadata["title"] = q_title

    content = ""
    q = db.query(qs,**metadata)
    
    while len(q) <= q_end and not q.done:
        time.sleep(.05)
        q.update()

    l = len(q)
    if q_end > l:
        q_end = l
    status += "%d total hits. aggregating." % (l)

    last_doc = -1
    collocates = {}
    text_file = None
    
    yield("<html>\n")
    yield("<head>")
    yield("<title>%s: collocation table for \"%s\"</title>" % (dbname, qs))
    #opensearch metadata in meta tags here.
    #total length, start index, hits per page.
    yield("</head>\n")
    yield("<body>\n")
    yield("<p class='description'>%s</p>\n" % status)
    if l > 0:
        for hit in q:
            doc_id = q.get_doc(hit)
            offsets = q.get_bytes(hit)
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

        yield("<table class='philologic_collocation'>\n")
        for n,f in sorted(collocates.items(),key=lambda x:x[1],reverse=True):
            url = "./?query=%s&author=%s&title=%s&colloc_filter=%s" % (qs,q_author,q_title,n)
            yield("  <tr class='philologic_collocation_row'>\n")
            yield("    <td class='philologic_collocation_key'><a href='%s'>%s</a></td>\n" % (url,n))
            yield("    <td class='philologic_collocation_value'>%s</td>\n" % f)
            yield("  </tr>\n")
        yield("</table>\n")


    yield("</body>")
    yield("</html>")

if __name__ == "__main__":
    CGIHandler().run(colloc_service)
