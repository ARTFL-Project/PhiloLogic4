#!/usr/bin/env python

from wsgiref.handlers import CGIHandler
from wsgiref.util import shift_path_info
from philologic.PhiloDB import PhiloDB
from philologic.DirtyFormatter import Formatter
from philologic import shlaxtree 
import urlparse
import re

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
    metadata_fields = db.locals["metadata_fields"]
    for p in metadata_fields:
        if p in environ["parsed_params"]:
            qdict[p] = environ["parsed_params"][p][0]
    if qdict:
        objects = db.metadata_query(**qdict)
    else:
        objects = db.toms.get_documents()
    yield "<html><head><title>%s</title></head>\n" % "bibliographic search results"
    yield "<body>\n"
    yield "<div class='philologic_cite_list'>\n"
    for o in objects:
        id = o["philo_id"].split(" ")
        url = "./" + "/".join(id)
        hit = [int(x) for x in id]
        yield db.locals["make_cite"](db,hit,url)
        yield "<br/>"
        count += 1
    yield "</div>\n"
    
    yield "<p class='description'>%d objects found</p>" % count    
    yield "</body>\n</html>\n"
    return

if __name__ == "__main__":
    CGIHandler().run(cite_list_service)
