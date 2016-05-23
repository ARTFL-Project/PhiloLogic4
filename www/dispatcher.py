#!/usr/bin/env python
"""Routing for PhiloLogic4."""

import datetime
import os
from cgi import FieldStorage
from random import randint
from wsgiref.handlers import CGIHandler

from philologic.DB import DB

import reports
from webApp import angular
from philologic.app import WSGIHandler
from philologic.app import WebConfig


def philo_dispatcher(environ, start_response):
    """Dispatcher function."""
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)))
    request = WSGIHandler(environ, config)
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
            report = FieldStorage().getvalue('report')
            yield ''.join([i for i in getattr(reports, report or "concordance")(environ, start_response)])
    else:
        yield angular(environ, start_response)


if __name__ == "__main__":
    CGIHandler().run(philo_dispatcher)
    if randint(0, 1000) == 0:
        path = os.path.abspath(os.path.dirname(__file__)) + '/data/hitlists/'
        for filename in [path + i for i in os.listdir(path)]:
            file_modified = datetime.datetime.fromtimestamp(os.path.getmtime(filename))
            if datetime.datetime.now() - file_modified > datetime.timedelta(hours=1):
                os.remove(filename)
