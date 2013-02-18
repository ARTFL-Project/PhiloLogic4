#!/usr/bin/env python

from wsgiref.handlers import CGIHandler
from wsgiref.util import shift_path_info
from philologic.PhiloDB import PhiloDB
from philologic.DirtyFormatter import Formatter
from philologic import shlaxtree 
import urlparse
import re

metadata_params = ["author","title"]

def cite_list_service(environ, start_response):
    status = '200 OK' # HTTP Status
    headers = [('Content-type', 'text/html;charset=UTF-8')] # HTTP Headers
    start_response(status, headers)
    environ["parsed_params"] = urlparse.parse_qs(environ["QUERY_STRING"],keep_blank_values=True)
    if "philologic_dbname" in environ:
        dbname = environ["philologic_dbname"]
    else:
        dbname = environ["parsed_params"]["philologic_dbname"][0]    
    myname = environ["SCRIPT_NAME"]
    dbfile = "/var/lib/philologic/databases/" + dbname
    db = PhiloDB(dbfile,7)
    qdict = {}
    count = 0
    for p in metadata_params:
        if p in environ["parsed_params"]:
            qdict[p] = environ["parsed_params"][p][0]
    if qdict:
        objects = db.toms.query(**qdict)
    else:
        objects = db.toms.get_documents()
    yield "<html><head><title>%s</title></head>\n" % "bibliographic search results"
    yield "<body>\n"
    yield "<div class='philologic_cite_list'>\n"
    for o in objects:
        author = o["author"]
        title = o["title"]
        filename = o["filename"]
        id = o["philo_id"]
        url = "./" + "/".join(id.split(" "))
        yield "<a class='philologic_cite' href='%s'>" % url
        yield "<span class='philologic_property' title='author'>%s</span>, " % author
        yield "<span class='philologic_property' title='title'>%s</span>: " % title
        yield "<span class='philologic_property' title='filename'>%s</span>" % filename
        yield "</a><br/>\n"
        count += 1
    yield "</div>\n"
    
    yield "<p class='description'>%d objects found</p>" % count    
    yield "</body>\n</html>\n"
    return

if __name__ == "__main__":
    CGIHandler().run(cite_list_service)
