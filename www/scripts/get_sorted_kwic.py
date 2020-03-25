#!/usr/bin/env python3

import rapidjson
import os
from wsgiref.handlers import CGIHandler

from philologic.runtime.DB import DB
from philologic.runtime import kwic_hit_object, page_interval
from philologic.utils import sort_list

import sys

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


def get_sorted_kwic(environ, start_response):
    status = "200 OK"
    headers = [("Content-type", "application/json; charset=UTF-8"), ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace("scripts", ""))
    db = DB(config.db_path + "/data/")
    input_object = json.loads(environ["wsgi.input"].read().decode("utf8", "ignore"))
    all_results = input_object["results"]
    query_string = input_object["query_string"]
    sort_keys = [i for i in input_object["sort_keys"] if i]
    environ["QUERY_STRING"] = query_string
    request = WSGIHandler(environ, config)
    sorted_hits = get_sorted_hits(
        all_results, sort_keys, request, config, db, input_object["start"], input_object["end"]
    )
    yield rapidjson.dumps(sorted_hits).encode("utf8")


def get_sorted_hits(all_results, sort_keys, request, config, db, start, end):
    hits = db.query(request["q"], request["method"], request["arg"], **request.metadata)
    start, end, n = page_interval(request.results_per_page, hits, start, end)
    kwic_object = {
        "description": {"start": start, "end": end, "results_per_page": request.results_per_page},
        "query": dict([i for i in request]),
    }

    kwic_results = []
    for index in sort_list(all_results, sort_keys)[start:end]:
        hit = hits[index["index"]]
        kwic_result = kwic_hit_object(hit, config, db)
        kwic_results.append(kwic_result)

    kwic_object["results"] = kwic_results
    kwic_object["results_length"] = len(hits)
    kwic_object["query_done"] = hits.done

    return kwic_object


if __name__ == "__main__":
    CGIHandler().run(get_sorted_kwic)
