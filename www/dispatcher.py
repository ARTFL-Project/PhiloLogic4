#!/usr/bin/env python

import sys
import reports
import traceback as tb
from functions.log_config import *
from functions import access_control
from wsgiref.handlers import CGIHandler
from cgi import FieldStorage
from functions import clean_hitlists

def philo_dispatcher(environ,start_response):
    report = FieldStorage().getvalue('report')
    access = access_control(environ, start_response)
    if access:
        try:
            try:
                path_components = [c for c in environ["PATH_INFO"].split("/") if c]
            except:
                path_components = []
            if path_components:
                yield getattr(reports, report or "navigation")(environ,start_response)
            elif environ["QUERY_STRING"]:
                yield getattr(reports, report or "concordance")(environ,start_response)   
            else:
                yield reports.landing_page(environ,start_response)
            logging.info("%s\t%s" %  (os.environ["REMOTE_ADDR"], environ["QUERY_STRING"]))
        except Exception as e:
            logging.error("Query string: %s" % environ["QUERY_STRING"], exc_info=True)
            yield getattr(reports, "error")(environ,start_response)
    else:
        yield getattr(reports, 'access')(environ, start_response)
        
if __name__ == "__main__":
    CGIHandler().run(philo_dispatcher)
    clean_hitlists()
