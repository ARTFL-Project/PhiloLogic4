#!/usr/bin/env python3

import json
import os
from wsgiref.handlers import CGIHandler

from philologic.runtime.DB import DB

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


OBJECT_LEVEL = {"doc": 6, "div1": 5, "div2": 4, "div3": 3, "para": 2, "sent": 1}


def get_total_doc_count(environ, start_response):
    status = "200 OK"
    headers = [("Content-type", "application/json; charset=UTF-8"), ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace("scripts", ""))
    db = DB(config.db_path + "/data/")
    request = WSGIHandler(environ, config)
    hits = db.query(request["q"], request["method"], request["arg"], raw_results=True, **request.metadata)
    docs = set()
    hits.finish()
    total_results = 0
    zeros_to_append = " ".join("0" for _ in range(OBJECT_LEVEL[config["hitlist_stats"]["object_level"]]))
    for hit in hits:
        docs.add(f'''"{hit[0]} {zeros_to_append}"''')
        total_results += 1
    stats = []
    citations = []
    cursor = db.dbh.cursor()
    for field in config["hitlist_stats"]["fields"]:
        cursor.execute(f"SELECT COUNT(DISTINCT {field}) FROM toms WHERE philo_id IN ({', '.join(docs)})")
        count = cursor.fetchone()[0]
        stats.append({"field": field, "count": count})
    yield json.dumps({"total_results": total_results, "stats": stats}).encode("utf8")


if __name__ == "__main__":
    CGIHandler().run(get_total_doc_count)
