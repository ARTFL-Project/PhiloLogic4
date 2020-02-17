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
    if request.no_q:
        if request.no_metadata:
            hits = db.get_all(db.locals["default_object_level"], request["sort_order"], raw_results=True)

        else:
            hits = db.query(sort_order=request["sort_order"], raw_results=True, **request.metadata)
        if "title" in config["hitlist_stats"]["fields"]:
            config["hitlist_stats"]["fields"].remove("title")
    else:
        hits = db.query(request["q"], request["method"], request["arg"], raw_results=True, **request.metadata)
    docs = set()
    hits.finish()
    total_results = 0
    zeros_to_append = " ".join("0" for _ in range(OBJECT_LEVEL[config["stats_report_config"]["object_level"]]))
    for hit in hits:
        docs.add(f'''"{hit[0]} {zeros_to_append}"''')
        total_results += 1
    stats = []
    cursor = db.dbh.cursor()
    for field_obj in config["stats_report_config"]["fields"]:
        if field_obj["field"] == "title":
            count = len(docs)
        else:
            cursor.execute(
                f"SELECT COUNT(0) FROM (SELECT DISTINCT {field_obj['field']} FROM toms WHERE philo_id IN ({', '.join(docs)}))"  # we also count NULLs as distinct
            )
            count = cursor.fetchone()[0]
        stats.append({"field": field_obj["field"], "count": count})
    yield json.dumps({"total_results": total_results, "stats": stats}).encode("utf8")


if __name__ == "__main__":
    CGIHandler().run(get_total_doc_count)
