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
    hits = db.query(request["q"], request["method"], request["arg"], **request.metadata)
    cache_path = get_cache_path(request, db)
    if os.path.exists(f"{cache_path}.sorted"):
        yield rapidjson.dumps({"hits_done": len(hits), "cache_path": cache_path}).encode("utf8")
    else:
        fields = ["index", "left", "right", "q"] + config.kwic_metadata_sorting_fields
        if not os.path.exists(cache_path):
            with open(cache_path, "w") as cache_file:
                print("\t".join(fields), file=cache_file)
        cursor = db.dbh.cursor()
        with open(cache_path, "a") as cache_file:
            for hit in hits[index:]:
                sentence = " ".join(map(str, hit.hit[:6])) + " 0"
                cursor.execute("SELECT words FROM sentences WHERE philo_id = ?", (sentence,))
                words = msgpack.loads(lz4.frame.decompress(cursor.fetchone()[0]))
                left_side_text = []
                right_side_text = []
                query_words = []
                for word in words:
                    if hit.bytes[0] > word["start_byte"]:
                        left_side_text.append(word["word"])
                    elif word["start_byte"] > hit.bytes[-1]:
                        right_side_text.append(word["word"])
                    else:
                        query_words.append(word["word"])
                left_side_text = left_side_text[-10:]
                left_side_text.reverse()
                if not left_side_text:
                    left_side_text = ["zzzzzzz" for _ in range(10)]  # make sure we sort last if no words before: DP
                if not right_side_text:
                    right_side_text = ["zzzzzzz" for _ in range(10)]  # make sure we sort last if no words after
                result_obj = {
                    "right": ",".join(right_side_text[:10]),
                    "left": ",".join(left_side_text),
                    "q": ",".join(query_words),
                    "index": index,
                }
                for metadata in config.kwic_metadata_sorting_fields:
                    result_obj[metadata] = ",".join(hit[metadata].lower().split())
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
