#!/usr/bin/env python

from wsgiref.handlers import CGIHandler
from wsgiref.util import shift_path_info
from philologic.PhiloDB import PhiloDB
from philologic.DirtyFormatter import Formatter
from philologic import shlaxtree 
import urlparse
import re

myformat = {}

myformat["p"] = "\n<p/>"
myformat["/p"] = ""
myformat["br"] = "<br/>\n"
myformat["span"] = "<span>"
myformat["/span"] = "</span>"
myformat["s"] = ""
myformat["/s"] = ""
myformat["/l"] = "<br/>\n"
myformat["/ab"] = "<br/>\n"
f = Formatter(myformat)

def object_service(environ, start_response):
    status = '200 OK' # HTTP Status
    headers = [('Content-type', 'text/html;charset=UTF-8')] # HTTP Headers
    start_response(status, headers)
    environ["parsed_params"] = urlparse.parse_qs(environ["QUERY_STRING"],keep_blank_values=True)
    # a wsgi app is supposed to return an iterable;
    # yielding lets you stream, rather than generate everything at once.
    if "philologic_dbname" in environ:
        dbname = environ["philologic_dbname"]
    else:
        dbname = environ["parsed_params"]["philologic_dbname"][0]
    myname = environ["SCRIPT_NAME"]
    dbfile = "/var/lib/philologic/databases/" + dbname
    db = PhiloDB(dbfile,7)
    print >> environ['wsgi.errors'],"opened toms"
    if "philologic_id" in environ:
        obj_string = environ["philologic_id"]
    else:
        obj_string = environ["parsed_params"]["object_id"][0]
    obj_split = [o  for o in obj_string.split("/") if o != ""]
    obj = []
    count = 0

    while obj_split:
        p = obj_split.pop(0)
        obj.append(p)
            
    status = "" 
    filename = ""
    start = 0
    end = 0
    length = 0

    doc_id = obj[0]
    filename = db.toms[doc_id]["filename"]
#    author = db.toms[doc_id]["author"]
#    title = db.toms[doc_id]["title"]
    url = myname + "/" + "/".join(obj)

    yield("<html>\n")
    yield("<head>")
    yield("<title>%s: %s</title>" % (dbname, obj))
    #opensearch metadata in meta tags here.
    #total length, start index, hits per page.
    yield("</head>\n")
    yield("<body>\n")
    yield("<div class='philologic_object'>\n")
    yield("<p class='description'>%s</p>\n" % status)    
#    yield("<p class='description'>%s</p>\n" % str(environ))

    content = ""
    content += "<div class='context_container' id='%s'>" % doc_id #still isn't balanced.
    # the cite should be in standard format like in the concordance.
    content += db.locals["make_cite"](db,obj,url)
#    content += "<a class='cite' href='%s'>%s, %s</a><br/>" % (url,author,title)

    for r in range(1,len(obj) + 1):
        parent = obj[:r]
        if parent in db.toms:
            o = db.toms[parent]
            filename = o["filename"] or filename
            start = o["byte_start"] or start
            end = o["byte_end"] or end

    status += " " + repr((filename,length,start,end))
    file = "/var/lib/philologic/databases/%s/TEXT/%s" % (dbname,filename)
    fh = open(file)
    fh.seek(start)
    chunk = fh.read(end - start)
    
    if "word_offset" in environ["parsed_params"]:
        word_offset =  int(environ["parsed_params"]["word_offset"][0])
        if word_offset >= start and word_offset <= end:
            breakpoint = word_offset - start
            left = chunk[:breakpoint]
            rest = chunk[breakpoint:]
            word,right = re.split("[\s.;:,<>?!]",rest,1)    
            content += f.format(left + "<span rend='preserve' class='hilite'>" + word + "</span> " + right)
    else:
        content += db.locals["format_stream"](chunk)

    yield content
    yield "</div>\n"

#    prev,next = db.toms.get_prev_next(o)

    if prev:
        prev_url = myname + "/" + "/".join(prev["philo_id"].split(" "))
        prev_link = "<a class='cite' style='float:left;' href='%s'>%s</a>" % (prev_url,"&lt;Back")
    else:
        prev_link = ""

    if next:
        next_url = myname + "/" + "/".join(next["philo_id"].split(" "))
        next_link = "<a class='cite' style='float:right;' href='%s'>%s</a>" % (next_url, "Next&gt;")
    else:
        next_link = ""

    link_clear = "<span style='clear:both'>PhiloLogic 4.0 BETA </span>"
    yield "<div class='more'>" + prev_link + next_link + link_clear + "</div>\n"
    yield "</body>\n"
    yield "</html>"

if __name__ == "__main__":
    CGIHandler().run(object_service)
