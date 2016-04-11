#!/usr/bin/env python
"""Routing for PhiloLogic4."""

from cgi import FieldStorage
from wsgiref.handlers import CGIHandler

from philologic.DB import DB

import functions as f
import reports
from functions import clean_hitlists
from functions.wsgi_handler import WSGIHandler


def philo_dispatcher(environ, start_response):
    """Dispatcher function."""
    report = FieldStorage().getvalue('report')
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    if request.content_type == "application/json":
        try:
            path_components = [c for c in environ["PATH_INFO"].split("/") if c]
        except:
            path_components = []
        if path_components:
            if path_components[-1] == "table-of-contents":
                yield ''.join([i for i in reports.table_of_contents(environ, start_response)])
            else:
                yield ''.join([i for i in getattr(reports, "navigation")(environ, start_response)])
        else:
            yield ''.join([i for i in getattr(reports, report or "concordance")(environ, start_response)])
    else:
        yield f.webApp.angular(environ, start_response)


if __name__ == "__main__":
    CGIHandler().run(philo_dispatcher)
    clean_hitlists()
