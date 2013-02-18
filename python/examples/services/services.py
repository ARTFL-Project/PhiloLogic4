#!/usr/bin/env python
from wsgiref.handlers import CGIHandler
from wsgiref.util import shift_path_info
from philologic.PhiloDB import PhiloDB
from philologic.DirtyFormatter import Formatter
from philologic import shlaxtree 
from sqlite3 import OperationalError
import urlparse
import re
import sys
import urllib

from object_service import object_service
from conc_service import conc_service
from form_service import form_service
from cite_list_service import cite_list_service
from object_children_service import object_children_service
from freq_service import freq_service
from freq_json_service import freq_json_service
from colloc_service import colloc_service
from colloc_filter_service import colloc_filter_service

def philo_dispatcher(environ,start_response):
    environ["parsed_params"] = urlparse.parse_qs(environ["QUERY_STRING"],keep_blank_values=True)
    cgi = environ["parsed_params"]

    dbname = shift_path_info(environ)
    environ["philologic_dbname"] = dbname
    myname = environ["SCRIPT_NAME"]
    print >> sys.stderr, myname
    dbfile = "/var/lib/philologic/databases/" + dbname
    print >> sys.stderr, dbfile
    try:
        db = PhiloDB(dbfile,7)
    except OperationalError:
        return

    environ["philologic_dbname"] = dbname

    if environ["PATH_INFO"]:
        print >> sys.stderr, "scanning path info"
        scanned = environ["PATH_INFO"].split("/")
        scanned = [i for i in scanned if i is not ""]
        print >> sys.stderr, "%s scanned." % repr(scanned)
        if "children" in scanned:
            environ["philologic_id"] = environ["PATH_INFO"]
            return object_children_service(environ,start_response)
        elif "form" in scanned:
            return form_service(environ,start_response)
        elif scanned:
            environ["philologic_id"] = environ["PATH_INFO"]
            print >> sys.stderr, "passing to object formatter"
            return object_service(environ,start_response)
        
        
    if "query" in cgi and cgi["query"][0]:
        if "report" in cgi:
            if cgi["report"][0] == "frequency":
                if "json" in cgi:
                    if "field" in cgi and cgi["field"][0] == "collocates":
                        from colloc_json_service import colloc_json_service
                        return colloc_json_service(environ,start_response)
                    return freq_json_service(environ,start_response)
                return freq_service(environ,start_response)
            elif cgi["report"][0] == "collocation":
                if "json" in cgi:
                    from colloc_json_service import colloc_json_service
                    return colloc_json_service(environ,start_response)
                return colloc_service(environ,start_response)
            return conc_service(environ,start_response)
        elif "colloc_filter" in cgi:
            return colloc_filter_service(environ,start_response)
        else:
            return conc_service(environ,start_response)

    else:
        return cite_list_service(environ,start_response)

if __name__ == "__main__":
    CGIHandler().run(philo_dispatcher)
