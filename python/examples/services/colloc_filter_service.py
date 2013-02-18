#!/usr/bin/env python

from wsgiref.handlers import CGIHandler
from wsgiref.util import shift_path_info
from philologic.PhiloDB import PhiloDB
from philologic.DirtyFormatter import Formatter
from philologic import shlaxtree 
import time
import urlparse
import re
from philo_helpers import *

def transform(node):
    if node.attrib.get("class","") != "hilite" and node.attrib.get("class","") != "philologic_context": 
        node.tag = None
    if node.text: node.text = re.sub(r"\s+", " ",node.text).decode("utf-8","ignore") # ignore leading/trailing malformed chars.
    if node.tail: node.tail = re.sub(r"\s+", " ",node.tail).decode("utf-8","ignore")
    for child in node:
        transform(child)

def colloc_filter_service(environ, start_response):
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
    q_end = int(environ["parsed_params"].get('q_end',[0])[0]) or q_start + 49  
    width = int(environ["parsed_params"].get("width",[0])[0]) or 100
    query_method = environ["parsed_params"].get("query_method",[0])[0] or None
    query_arg = environ["parsed_params"].get("query_arg",[0])[0] or 0
    
    q_title = environ["parsed_params"].get("title",[""])[0] or ""
    q_author = environ["parsed_params"].get("author",[""])[0] or ""
    filter_word = environ["parsed_params"]["colloc_filter"][0]
    status = "running query for %s @ %s: " % (qs,dbname)

    metadata = {}
    if q_author:
        metadata["author"] = q_author
    if q_title:
        metadata["title"] = q_title

    metadata_fields = ["author","title","date"]
    query_metadata = {}
    
    for meta_f in metadata_fields:
        if meta_f in environ["parsed_params"]:
            query_metadata[meta_f] = environ["parsed_params"][meta_f][0]    

    content = ""
    q = db.query(qs,query_method,query_arg,**query_metadata)
    
    while len(q) <= q_end and not q.done:
        time.sleep(.05)
        q.update()

    l = len(q)
    if q_end > l:
        q_end = l
    status += "%d total hits. filtering for '%s'." % (l,filter_word)

    last_doc = -1
    collocates = {}
    text_file = None
    
    yield("<html>\n")
    yield("<head>")
    yield("<title>%s: collocation results %d to %d for \"%s\" filtered by \"%s\"</title>" % (dbname, q_start,q_end,qs, filter_word))
    #opensearch metadata in meta tags here.
    #total length, start index, hits per page.
    yield("</head>\n")
    yield("<body>\n")
    yield "<div class='philologic_concordance'>"
    yield("<p class='description'>%s</p>\n" % status)
    if l > 0:
        f_count = 0
        yield "<ol start='%d'>\n" % q_start
        for hit in q:
            doc_id = q.get_doc(hit)
            offsets = q.get_bytes(hit)
            offsets.sort()
            first_offset = offsets[0]
            filename = db.toms[doc_id]["filename"]
            author = db.toms[doc_id]["author"]
            title = db.toms[doc_id]["title"]                        
            date = db.toms[doc_id]["date"]
            
            url_comps = [str(doc_id)]
            for id_comp in hit[1:]:
                id_comp = str(id_comp)
                if url_comps + [id_comp] in db.toms:
                    url_comps += [id_comp]
            url = "/".join(["."] + url_comps )

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
            if filter_word in [t.group(2) for t in list(re.finditer(r"(<[^>]+>)|(\w+)",text))[1:-1]]:
                # then we have a virtual "hit":
                f_count += 1
                if f_count < q_start:
                    pass
                elif f_count > q_end:
                    break
                else:
                    yield "<li class='philologic_occurence'>"
    
                    yield "<a href='%s' class='philologic_cite'>" % url # should be a link
                    yield "<span class='philologic_property' title='author'>%s</span>, " % author
                    yield "<span class='philologic_property' title='title'>%s</span>: " % title
                    yield "<span class='philologic_property' title='date'>(%s)</span>" % date
                    yield "</a>\n"
    
                    p_start = conc_start - len("<div class='philologic_context'>...") + l_trim_off
                    parser = shlaxtree.TokenizingParser(p_start,offsets)
                    parser.feed("<div class='philologic_context'>..." + text + "...</div>\n")
                    tree = parser.close()
                    transform(tree)
                    context = shlaxtree.ElementTree.tostring(tree,encoding='utf-8')
                    yield context
                    yield "</li>\n"

        yield "</ol>"
        query_metadata["colloc_filter"] = filter_word
        next_url = make_link(qs,query_method,query_arg,q_end + 1,q_end + 50, **query_metadata)
        yield "<a href='%s'>more</a>" % next_url
    yield "</div>"
    yield("</body>")
    yield("</html>")
    
if __name__ == "__main__":
    CGIHandler().run(colloc_filter_service)

