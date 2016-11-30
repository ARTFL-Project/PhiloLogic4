#!/usr/bin/env python
"""Routing for PhiloLogic4."""

from __future__ import absolute_import
import datetime
import os
from cgi import FieldStorage
from random import randint
from wsgiref.handlers import CGIHandler

from philologic.runtime import WebConfig, WSGIHandler

import reports
from webApp import angular

path = os.path.abspath(os.path.dirname(__file__))


def philo_dispatcher(environ, start_response):
    """Dispatcher function."""
    config = WebConfig(path)
    request = WSGIHandler(environ, config)
    if request.content_type == "application/json" or request.format == "json":
        try:
            path_components = [c for c in environ["PATH_INFO"].split("/") if c]
        except:
            path_components = []
        if path_components:
            if path_components[-1] == "table-of-contents":
                yield ''.join([i for i in reports.table_of_contents(environ, start_response)])
            else:
                yield ''.join([i for i in reports.navigation(environ, start_response)])
        else:
            report = getattr(reports, FieldStorage().getvalue('report'))
            yield ''.join([i for i in report(environ, start_response)])
    else:
        yield angular(environ, start_response)


if __name__ == "__main__":
    CGIHandler().run(philo_dispatcher)
    # clean-up hitlist every now and then
    if randint(0, 1000) == 0:
        hit_list_path = os.path.join(path, '/data/hitlists/')
        for filename in [os.path.join(hit_list_path, i) for i in os.listdir(hit_list_path)]:
            file_modified = datetime.datetime.fromtimestamp(os.path.getmtime(filename))
            if datetime.datetime.now() - file_modified > datetime.timedelta(hours=1):
                os.remove(filename)
