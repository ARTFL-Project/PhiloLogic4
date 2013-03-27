#!/usr/bin/env python

from wsgiref.handlers import CGIHandler
from wsgiref.util import shift_path_info
from philologic.PhiloDB import PhiloDB
from philologic.DirtyFormatter import Formatter
from philologic import shlaxtree
import urlparse
import re
import sys

metadata_params = ["author","title","filename","head"]

def object_children_service(environ, start_response):
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
    obj_split = [o for o in obj_string.split("/") if (o != "" and o != "children")]
    obj = []
    count = 0

    while obj_split:
        p = obj_split.pop(0)
        obj.append(p)
            
    yield "<html><head><title>children for %s</title></head>\n" % str(obj)
    yield "<body>\n"
    yield "<div class='philologic_cite_list'>\n"
    for child in db.toms.get_children(obj):  
        url = "./" + "/".join(child["philo_id"].split(" "))
        yield "<a class='philologic_cite' href='%s'>" % url
        for p in metadata_params:
            if child[p]:        
                yield "<span class='philologic_property' title='%s'>%s</span>, " % (p, child[p])
        yield "</a><br/>\n"
    yield "</div>\n</body>\n</html>"
    
if __name__ == "__main__":
    CGIHandler().run(object_children_service)
