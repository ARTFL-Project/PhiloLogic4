#!/usr/bin/env python3
"""Output results in JSON or CSV"""

import csv
import io
import os
import sys
from orjson import dumps
import re
from wsgiref.handlers import CGIHandler

sys.path.append("..")
import custom_functions

try:
    from custom_functions import WebConfig
except ImportError:
    from philologic.runtime import WebConfig
try:
    from custom_functions import WSGIHandler
except ImportError:
    from philologic.runtime import WSGIHandler
try:
    from custom_functions import bibliography_results
except ImportError:
    from philologic.runtime import bibliography_results
try:
    from custom_functions import concordance_results
except ImportError:
    from philologic.runtime import concordance_results
try:
    from custom_functions import kwic_results
except ImportError:
    from philologic.runtime import kwic_results
try:
    from custom_functions import collocation_results
except ImportError:
    from philologic.runtime import collocation_results
try:
    from custom_functions import generate_time_series
except ImportError:
    from philologic.runtime import generate_time_series
try:
    from custom_functions import aggregation_by_field
except ImportError:
    from philologic.runtime import aggregation_by_field


TAGS = re.compile(r"<[^>]+>")
NEWLINES = re.compile(r"\n+")
SPACES = re.compile(r"\s{2,}")


def export_results(environ, start_response):
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace("scripts", ""))
    request = WSGIHandler(environ, config)
    results = []
    if request.report == "bibliography":
        results = bibliography_results(request, config)["results"]
    if request.report == "concordance":
        for hit in concordance_results(request, config)["results"]:
            hit_to_save = {
                "metadata_fields": {**hit["metadata_fields"], "philo_id": hit["philo_id"]},
                "context": hit["context"],
            }
            if request.filter_html == "true":
                hit_to_save["context"] = filter_html(hit["context"])
            results.append(hit_to_save)
    elif request.report == "kwic":
        for hit in kwic_results(request, config)["results"]:
            hit_to_save = {
                "metadata_fields": {**hit["metadata_fields"], "philo_id": hit["philo_id"]},
                "context": hit["context"],
            }
            if request.filter_html == "true":
                hit_to_save["context"] = filter_html(hit["context"])
            results.append(hit_to_save)
    elif request.report == "collocation":
        results_object = collocation_results(request, config)["collocates"]
    elif request.report == "time_series":
        results_object = generate_time_series(request, config)["results"]
    elif request.report == "aggregation":
        results_object = aggregation_by_field(request, config)["results"]

    if request.output_format == "json":
        status = "200 OK"
        headers = [("Content-type", "application/json; charset=UTF-8"), ("Access-Control-Allow-Origin", "*")]
        start_response(status, headers)
        yield dumps(results)
    elif request.output_format == "csv":
        status = "200 OK"
        headers = [("Content-type", "text/csv; charset=UTF-8"), ("Access-Control-Allow-Origin", "*")]
        start_response(status, headers)
        yield csv_output(results).encode("utf8")


def filter_html(html):
    """Strip out all HTML"""
    text = TAGS.sub("", html).strip()
    text = NEWLINES.sub(" ", text)
    text = SPACES.sub(" ", text)
    return text


def csv_output(results):
    """Convert results to CSV representation"""
    output_string = io.StringIO()
    writer = csv.DictWriter(
        output_string, fieldnames=["context", *sorted([field for field in results[0]["metadata_fields"].keys()])]
    )
    writer.writeheader()
    for result in results:
        writer.writerow({**result["metadata_fields"], "context": result["context"]})
    return output_string.getvalue()


if __name__ == "__main__":
    CGIHandler().run(export_results)
