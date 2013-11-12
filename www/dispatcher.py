#!/usr/bin/env python

import os
import sys
import urlparse
import reports
from wsgiref.handlers import CGIHandler
from cgi import FieldStorage
from functions import clean_hitlists

def philo_dispatcher(environ,start_response):
    report = FieldStorage().getvalue('report')
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
        
if __name__ == "__main__":
    CGIHandler().run(philo_dispatcher)
    clean_hitlists()
