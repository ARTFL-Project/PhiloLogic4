#!/usr/bin/env python3
"""Routing for PhiloLogic4."""


import datetime
import os
from asyncio import get_event_loop
from cgi import FieldStorage
from random import randint
from glob import glob
from wsgiref.handlers import CGIHandler

from philologic.runtime import WebConfig, WSGIHandler

import reports
from webApp import angular

path = os.path.abspath(os.path.dirname(__file__))


def philo_dispatcher(environ, start_response):
    """Dispatcher function."""
    loop = get_event_loop()
    clean_task = loop.create_task(clean_up())
    config = WebConfig(path)
    request = WSGIHandler(environ, config)
    response = ""
    if request.content_type == "application/json" or request.format == "json":
        try:
            path_components = [c for c in environ["PATH_INFO"].split("/") if c]
        except:
            path_components = []
        if path_components:
            if path_components[-1] == "table-of-contents":
                response = "".join([i for i in reports.table_of_contents(environ, start_response)])
            else:
                response = "".join([i for i in reports.navigation(environ, start_response)])
        else:
            report = getattr(reports, FieldStorage().getvalue("report"))
            response = "".join([i for i in report(environ, start_response)])
    else:
        response = angular(environ, start_response)
    yield response.encode("utf8")
    loop.run_until_complete(clean_task)


async def clean_up():
    """clean-up hitlist every now and then"""
    rand = randint(0, 100)
    if rand == 1:
        hit_list_path = os.path.join(path, "data/hitlists/*")
        for filename in glob(hit_list_path):
            file_modified = datetime.datetime.fromtimestamp(os.path.getmtime(filename))
            if datetime.datetime.now() - file_modified > datetime.timedelta(hours=1):
                os.remove(filename)


if __name__ == "__main__":
    CGIHandler().run(philo_dispatcher)
