#!/usr/bin/env python3

import rapidjson
import os
from wsgiref.handlers import CGIHandler

from philologic5.runtime.DB import DB

import sys

sys.path.append("..")
import custom_functions

try:
    from custom_functions import WebConfig
except ImportError:
    from philologic5.runtime import WebConfig
try:
    from custom_functions import WSGIHandler
except ImportError:
    from philologic5.runtime import WSGIHandler


OBJECT_LEVEL = {"doc": 6, "div1": 5, "div2": 4, "div3": 3, "para": 2, "sent": 1}
OBJ_DICT = {"doc": 1, "div1": 2, "div2": 3, "div3": 4, "para": 5, "sent": 6, "word": 7}


def get_total_doc_count(environ, start_response):
    status = "200 OK"
    headers = [
        ("Content-type", "application/json; charset=UTF-8"),
        ("Access-Control-Allow-Origin", "*"),
    ]
    start_response(status, headers)
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace("scripts", ""))
    db = DB(config.db_path + "/data/")
    request = WSGIHandler(environ, config)
    if request.no_q:
        if request.no_metadata:
            hits = db.get_all(db.locals["default_object_level"], request["sort_order"], raw_results=True,)

        else:
            hits = db.query(sort_order=request["sort_order"], raw_results=True, **request.metadata)
    else:
        hits = db.query(request["q"], request["method"], request["arg"], raw_results=True, **request.metadata,)

    hits.finish()
    total_results = 0
    docs = [set() for _ in range(len(config["stats_report_config"]))]
    zeros_to_append = [
        " ".join("0" for _ in range(OBJECT_LEVEL[field["object_level"]])) for field in config["stats_report_config"]
    ]
    for hit in hits:
        for pos, field in enumerate(config["stats_report_config"]):
            obj_level = OBJ_DICT[field["object_level"]]
            docs[pos].add(f'''"{' '.join(map(str, hit[:obj_level]))} {zeros_to_append[pos]}"''')
        total_results += 1
    stats = []
    cursor = db.dbh.cursor()
    for pos, field_obj in enumerate(config["stats_report_config"]):
        if field_obj["field"] == "title":
            count = len(docs[pos])
        else:
            cursor.execute(
                f"SELECT COUNT(0) FROM (SELECT DISTINCT {field_obj['field']} FROM toms WHERE philo_id IN ({', '.join(docs[pos])}))"  # we also count NULLs as distinct
            )
            count = cursor.fetchone()[0]
        stats.append({"field": field_obj["field"], "count": count})
    yield rapidjson.dumps({"stats": stats}).encode("utf8")


if __name__ == "__main__":
    CGIHandler().run(get_total_doc_count)
