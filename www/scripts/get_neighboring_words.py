#!/usr/bin/env python3

import hashlib
import os
import sys
import timeit
from wsgiref.handlers import CGIHandler

import lz4.frame
import msgpack
import rapidjson
from philologic.runtime.DB import DB
import re

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

NUMBER = re.compile(r"\d")
OBJECT_LEVELS = {"doc": 1, "div1": 2, "div2": 3, "div3": 4, "para": 5}


def get_neighboring_words(environ, start_response):
    status = "200 OK"
    headers = [("Content-type", "application/json; charset=UTF-8"), ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace("scripts", ""))
    db = DB(config.db_path + "/data/")
    request = WSGIHandler(environ, config)
    try:
        index = int(request.hits_done)
    except:
        index = 0
    max_time = int(request.max_time)
    start_time = timeit.default_timer()

    fields = ["index", "left", "right", "q"]
    metadata_search = False
    if (
        request.first_kwic_sorting_option in ("left", "right", "q", "")
        and request.second_kwic_sorting_option in ("left", "right", "q", "")
        and request.third_kwic_sorting_option in ("left", "right", "q", "")
    ):  # fast path
        hits = db.query(request["q"], request["method"], request["arg"], raw_results=True, **request.metadata)
        # object_types = []
        # for field in config.kwic_metadata_sorting_fields:
        #     object_type = db.locals["metadata_types"][field]
        #     if object_type == "div":
        #         object_types.extend(["div1", "div2", "div3"])
        #     else:
        #         object_types.append(object_type)
    else:
        metadata_search = True
        hits = db.query(request["q"], request["method"], request["arg"], **request.metadata)
        fields.extend(config.kwic_metadata_sorting_fields)
    cache_path = get_cache_path(request, db)
    if os.path.exists(f"{cache_path}.sorted"):
        yield rapidjson.dumps({"hits_done": len(hits), "cache_path": cache_path}).encode("utf8")
    else:
        if not os.path.exists(cache_path):
            with open(cache_path, "w") as cache_file:
                print("\t".join(fields), file=cache_file)
        cursor = db.dbh.cursor()
        with open(cache_path, "a") as cache_file:
            for hit in hits[index:]:
                if metadata_search is False:
                    remaining = list(hit[7:])
                    offsets = []
                    while remaining:
                        remaining.pop(0)
                        if remaining:
                            offsets.append(remaining.pop(0))
                    offsets.sort()
                    sentence = " ".join(map(str, hit[:6])) + " 0"
                else:
                    offsets = hit.bytes
                    sentence = " ".join(map(str, hit.hit[:6])) + " 0"
                cursor.execute("SELECT words FROM sentences WHERE philo_id = ?", (sentence,))
                words = msgpack.loads(lz4.frame.decompress(cursor.fetchone()[0]))
                left_side_text = []
                right_side_text = []
                query_words = []
                for word in words:
                    if NUMBER.search(word["word"]):
                        continue
                    if offsets[0] > word["start_byte"]:
                        left_side_text.append(word["word"])
                    elif word["start_byte"] > offsets[-1]:
                        right_side_text.append(word["word"])
                    else:
                        query_words.append(word["word"])
                left_side_text = left_side_text[-10:]
                left_side_text.reverse()
                if not left_side_text:
                    left_side_text = ["zzzzzzz" for _ in range(10)]  # make sure we sort last if no words before
                if not right_side_text:
                    right_side_text = ["zzzzzzz" for _ in range(10)]  # make sure we sort last if no words after
                result_obj = {
                    "right": ",".join(right_side_text[:10]),
                    "left": ",".join(left_side_text),
                    "q": ",".join(query_words),
                    "index": index,
                }
                if metadata_search is True:
                    for metadata in config.kwic_metadata_sorting_fields:
                        result_obj[metadata] = ",".join(hit[metadata].lower().split())
                # else: object_ids = []
                # for object_type in object_types:
                #     object_id = list(hit[: OBJECT_LEVELS[object_type]])
                #     philo_id = object_id + [0 for _ in range(7 - len(object_id))]
                #     object_ids.append(" ".join(map(str, philo_id)))
                # cursor.execute(
                #     f"SELECT {','.join(config.kwic_metadata_sorting_fields)} FROM toms WHERE philo_type in ({','.join(object_types)}) AND philo_id"
                # )
                print("\t".join(str(result_obj[field]) for field in fields), file=cache_file)
                index += 1
                elapsed = timeit.default_timer() - start_time
                if (
                    elapsed > max_time
                ):  # avoid timeouts by splitting the query if more than 5 seconds has been spent in the loop
                    break
        yield rapidjson.dumps({"hits_done": index, "cache_path": cache_path}).encode("utf8")


def get_cache_path(request, db):
    hash = hashlib.sha1()
    hash.update(request["q"].encode("utf-8"))
    hash.update(request["method"].encode("utf-8"))
    hash.update(str(request["arg"]).encode("utf-8"))
    print(request.first_kwic_sorting_option, file=sys.stderr)
    hash.update(request.first_kwic_sorting_option.encode("utf-8"))
    hash.update(request.second_kwic_sorting_option.encode("utf-8"))
    hash.update(request.third_kwic_sorting_option.encode("utf-8"))
    for field, metadata in sorted(request.metadata.items(), key=lambda x: x[0]):
        hash.update(f"{field}: {metadata}".encode("utf-8"))
    cache_path = os.path.join(db.path, "hitlists", f"{hash.hexdigest()}.kwic")
    return cache_path


if __name__ == "__main__":
    CGIHandler().run(get_neighboring_words)
