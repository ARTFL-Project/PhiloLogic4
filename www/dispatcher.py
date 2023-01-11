#!/usr/bin/env python3
"""Routing for PhiloLogic4."""


import datetime
import os
from random import randint
from typing import Callable
from urllib.parse import parse_qs, urlparse
from wsgiref.handlers import CGIHandler

import reports
from philologic.runtime import WebConfig, WSGIHandler
from webApp import start_web_app

path = os.path.abspath(os.path.dirname(__file__))


def philo_dispatcher(environ, start_response):
    """Dispatcher function."""
    config = WebConfig(path)
    request = WSGIHandler(environ, config)
    if request.content_type == "application/json" or request.format == "json":
        try:
            path_components = [c for c in environ["PATH_INFO"].split("/") if c]
        except Exception:
            path_components = []
        if path_components:
            if path_components[-1] == "table-of-contents":
                yield b"".join(reports.table_of_contents(environ, start_response))
            else:
                yield b"".join(reports.navigation(environ, start_response))
        else:
            try:
                report_name: str = parse_qs(environ["QUERY_STRING"])["report"][0]
            except KeyError:
                report_name = urlparse(environ["REQUEST_URI"]).path.split("/")[-1]
            report: Callable = getattr(reports, report_name)
            yield b"".join(report(environ, start_response))
    elif request.full_bibliography is True:
        yield b"".join(reports.bibliography(environ, start_response))
    else:
        yield start_web_app(environ, start_response).encode("utf8")

    # clean-up hitlist every now and then
    if randint(0, 10) == 1:
        for file in os.scandir(os.path.join(path, "data/hitlists/*")):
            file_modified = datetime.datetime.fromtimestamp(os.path.getmtime(file.path))
            if datetime.datetime.now() - file_modified > datetime.timedelta(minutes=10):
                os.remove(file.path)


if __name__ == "__main__":
    CGIHandler().run(philo_dispatcher)
