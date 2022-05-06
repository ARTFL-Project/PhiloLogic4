#!/usr/bin/env python3

import orjson
import os
from wsgiref.handlers import CGIHandler

from philologic.runtime.DB import DB
from philologic.runtime import kwic_hit_object, page_interval

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
    """Get sorted KWIC"""
    status = "200 OK"
    headers = [("Content-type", "application/json; charset=UTF-8"), ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace("scripts", ""))
    db = DB(config.db_path + "/data/")
    request = WSGIHandler(environ, config)
    sorted_hits = get_sorted_hits(request, config, db)
    yield orjson.dumps(sorted_hits)


def get_sorted_hits(request, config, db):
    """Get sorted hits"""
    hits = db.query(request["q"], request["method"], request["arg"], **request.metadata)
    start, end, _ = page_interval(request.results_per_page, hits, request.start, request.end)
    kwic_object = {
        "description": {"start": start, "end": end, "results_per_page": request.results_per_page},
        "query": dict([i for i in request]),
    }
    if not os.path.exists(f"{request.cache_path}.sorted"):
        with open(request.cache_path) as cache:
            fields = cache.readline().strip().split("\t")
        sort_order = []
        if request.first_kwic_sorting_option:
            key = fields.index(request.first_kwic_sorting_option) + 1
            sort_order.append(f"-k {key},{key}")
        if request.second_kwic_sorting_option:
            key = fields.index(request.second_kwic_sorting_option) + 1
            sort_order.append(f"-k {key},{key}")
        if request.third_kwic_sorting_option:
            key = fields.index(request.third_kwic_sorting_option) + 1
            sort_order.append(f"-k {key},{key}")
        sort_order = " ".join(sort_order)
        os.system(
            f"tail -n +2 {request.cache_path} | sort {sort_order} > {request.cache_path}.sorted && rm {request.cache_path}"
        )  # no numeric sort since we would have to know the type of the field being sorted on: e.g. -k 2,2n
    kwic_results = []
    with open(f"{request.cache_path}.sorted") as sorted_results:
        for line_number, line in enumerate(sorted_results, 1):
            if line_number < start:
                continue
            if line_number > end:
                break
            index = int(line.split("\t")[0])
            hit = hits[index]
            kwic_result = kwic_hit_object(hit, config, db)
            kwic_results.append(kwic_result)

    kwic_object["results"] = kwic_results
    kwic_object["results_length"] = len(hits)
    kwic_object["query_done"] = hits.done

    return kwic_object


if __name__ == "__main__":
    CGIHandler().run(get_sorted_kwic)
