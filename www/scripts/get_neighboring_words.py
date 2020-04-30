#!/usr/bin/env python3

import rapidjson
import os
import string
import timeit
from wsgiref.handlers import CGIHandler

from philologic5.runtime.DB import DB

# from philologic5.runtime import kwic_hit_object
from philologic5.runtime.get_text import get_text
from philologic5.runtime.ObjectFormatter import format_strip, adjust_bytes, clean_tags
from philologic5.runtime.FragmentParser import parse as FragmentParserParse

import re
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


remove_punctuation_map = dict((ord(char), None) for char in string.punctuation if ord(char) != "'")


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

    kwic_words = []
    start_time = timeit.default_timer()
    hits = db.query(request["q"], request["method"], request["arg"], **request.metadata)

    token_regex = re.compile(fr"""{db.locals["token_regex"]}""")
    for hit in hits[index:]:
        # Determine length of text needed
        byte_distance = hit.bytes[-1] - hit.bytes[0]
        length = config.concordance_length + byte_distance + config.concordance_length

        # Get concordance and align it
        new_bytes, start_byte = adjust_bytes(hit.bytes, config.concordance_length)
        conc_text = get_text(hit, start_byte, length, config.db_path)
        left_side_text = split_text(conc_text[: new_bytes[0]], token_regex)[-10:]
        right_side_text = split_text(conc_text[new_bytes[0] :], token_regex)[:10]
        word = right_side_text[0]
        right_side_text = right_side_text[1:]
        left_side_text.reverse()

        result_obj = {
            "right": " ".join(right_side_text),
            "left": " ".join(left_side_text),
            "q": word,
            "index": index,
        }
        for metadata in config.kwic_metadata_sorting_fields:
            result_obj[metadata] = hit[metadata].lower()

        kwic_words.append(result_obj)

        index += 1

        elapsed = timeit.default_timer() - start_time
        if (
            elapsed > max_time
        ):  # avoid timeouts by splitting the query if more than 10 seconds has been spent in the loop
            break

    yield rapidjson.dumps({"results": kwic_words, "hits_done": index}).encode("utf8")


def split_text(text, token_regex):
    text = text.decode("utf8", "ignore")
    xml = FragmentParserParse(text)
    output = clean_tags(xml, token_regex)
    text = output.replace("\n", " ")
    text = text.replace("\r", "")
    text = text.replace("\t", " ")
    text = text.translate(remove_punctuation_map)
    return token_regex.findall(text.lower())


if __name__ == "__main__":
    CGIHandler().run(get_neighboring_words)
