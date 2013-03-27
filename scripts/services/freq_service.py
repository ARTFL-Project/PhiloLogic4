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
import urllib

def freq_service(environ,start_response):
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
    q_start = int(environ["parsed_params"].get('q_start',[0])[0]) or 1
    q_end = int(environ["parsed_params"].get('q_end',[0])[0]) or q_start + 2000 
    width = int(environ["parsed_params"].get("width",[0])[0]) or 100
    q_title = environ["parsed_params"].get("title",[""])[0] or ""
    q_author = environ["parsed_params"].get("author",[""])[0] or ""
    field = environ["parsed_params"].get("field",[""])[0] or "author"
    #need a field param.  author default?
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
    authors = {}
    titles = {}
        
    yield("<html>")
    yield("<head>")
    yield("<title>%s: frequency table for \"%s\"</title>" % (dbname, qs))
    #opensearch metadata in meta tags here.
    #total length, start index, hits per page.
    yield("</head>\n")
    yield("<body>\n")
    yield("<p class='description'>%s</p>\n" % status)
    if l > 0:
        for hit in q: #need to page q
            byte_offset = hit[6]
            offsets = list(hit[6:])
            offsets.reverse()
            
            doc_id = hit[0]
            if doc_id > last_doc:
                metadata = db.toms[doc_id]
            author = metadata["author"]
            title = metadata["title"]
    
            if author in authors:
                authors[author] += 1
            else:
                authors[author] = 1
            if title in titles:
                titles[title] += 1
            else:
                titles[title] = 1

        yield("<table class='philologic_frequency tablesorter' title='author'>\n")
        yield("<thead><tr class='philologic_frequency_header_row'><th>Author</th><th>Frequency</th></tr></thead>\n<tbody>")
        for n,f in sorted(authors.items(),key=lambda x:x[1], reverse=True):
            url = "./?query=%s&author=%s&title=%s" % (qs,n,q_title)
            yield("  <tr class='philologic_frequency_row'>\n")
            yield("    <td class='philologic_frequency_key'><a href='%s'>%s</a></td>\n" % (urllib.quote_plus(url,"/?&="),n)) #UGLY ENCODING HACK
            yield("    <td class='philologic_frequency_value'>%s</td>\n" % f)
            yield("  </tr>\n")
        yield("</tbody></table>\n")
        # shouldn't dump more than necessary.  go by field.  
        # should also have links to more pages of table.
#        yield("<table class='philologic_frequency' title='title'>\n")
#         for n,f in sorted(titles.items(),key=lambda x:x[1], reverse=True):
#             #url = "./?query=%s&author=%s&title=%s" % (qs,n,q_title)
#             yield("  <tr class='philologic_frequency_row'>\n")
#             yield("    <td class='philologic_frequency_key'><a href='%s'>%s</a></td>\n" % (url,n))
#             yield("    <td class='philologic_frequency_value'>%s</td>\n" % f)
#             yield("  </tr>\n")
#         yield("</table>\n")
    yield("</body>")
    yield("</html>")

if __name__ == "__main__":
    CGIHandler().run(freq_service)
