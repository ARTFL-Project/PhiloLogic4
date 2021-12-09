#!/usr/bin/env python3

import os
import sys
from wsgiref.handlers import CGIHandler

import rapidjson
from philologic.runtime.DB import DB

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
            hits = db.get_all(
                db.locals["default_object_level"],
                request["sort_order"],
                raw_results=True,
            )

        else:
            hits = db.query(sort_order=request["sort_order"], raw_results=True, **request.metadata)
    else:
        hits = db.query(
            request["q"],
            request["method"],
            request["arg"],
            raw_results=True,
            **request.metadata,
        )

    hits.finish()
    total_results = 0
    docs = [set() for _ in range(len(config["stats_report_config"]))]
    for hit in hits:
        for pos, field in enumerate(config["stats_report_config"]):
            docs[pos].add(tuple_to_str(hit, OBJ_DICT[field["object_level"]]))
        total_results += 1
    stats = []
    cursor = db.dbh.cursor()
    for pos, field_obj in enumerate(config["stats_report_config"]):
        if field_obj["field"] == "title":
            count = len(docs[pos])
        else:
            philo_type = db.locals["metadata_types"][field_obj["field"]]
            if philo_type != "div":
                cursor.execute(
                    f"SELECT COUNT(DISTINCT {field_obj['field']}) FROM toms WHERE philo_type='{philo_type}' AND philo_id IN ({', '.join(docs[pos])})"
                )
            else:
                cursor.execute(
                    f"SELECT COUNT(DISTINCT {field_obj['field']}) FROM toms WHERE philo_type IN ('div1', 'div2', 'div3') AND philo_id IN ({', '.join(docs[pos])})"
                )
            count = cursor.fetchone()[0]
            cursor.execute(
                f"SELECT COUNT(0) FROM (SELECT DISTINCT {field_obj['field']} FROM toms WHERE philo_id IN ({', '.join(docs[pos])}) AND {field_obj['field']} IS NULL)"
            )
            count += cursor.fetchone()[0]
        stats.append({"field": field_obj["field"], "count": count})
    yield rapidjson.dumps({"stats": stats}).encode("utf8")


def tuple_to_str(philo_id, obj_level):
    """Fast philo_id to str conversion:
    This is actually about 40-50% faster than a ' '.join(map(str, philo_id["obj_level]))"""
    if obj_level == 1:
        return f"'{philo_id[0]} 0 0 0 0 0 0'"
    elif obj_level == 2:
        return f"'{philo_id[0]} {philo_id[1]} 0 0 0 0 0'"
    elif obj_level == 3:
        return f"'{philo_id[0]} {philo_id[1]} {philo_id[2]} 0 0 0 0'"
    elif obj_level == 4:
        return f"'{philo_id[0]} {philo_id[1]} {philo_id[2]} {philo_id[3]} {philo_id[4]} 0 0 0'"


if __name__ == "__main__":
    CGIHandler().run(get_total_doc_count)
