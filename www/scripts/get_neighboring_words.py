#!/usr/bin/env python

import os
import sys
import timeit
from wsgiref.handlers import CGIHandler

import simplejson
from philologic.DB import DB

from philologic.app import WebConfig
from philologic.app import WSGIHandler


def get_neighboring_words(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'), ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)

    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace('scripts', ''))
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(environ, config)

    # Define whether we get words to the left or to the right or both
    # left = False
    # right = False
    # if request.first_kwic_sorting_option == "left" or request.second_kwic_sorting_option == "left" or request.third_kwic_sorting_option == "left":
    #     left = True
    # if request.first_kwic_sorting_option == "right" or request.second_kwic_sorting_option == "right" or request.third_kwic_sorting_option == "right":
    #     right = True
    try:
        index = int(request.hits_done)
    except:
        index = 0

    # Do we have metadata to extract?
    metadata_to_extract = []
    if request.first_kwic_sorting_option in db.locals.metadata_fields:
        metadata_to_extract.append(request.first_kwic_sorting_option)
    if request.second_kwic_sorting_option in db.locals.metadata_fields:
        metadata_to_extract.append(request.second_kwic_sorting_option)
    if request.third_kwic_sorting_option in db.locals.metadata_fields:
        metadata_to_extract.append(request.third_kwic_sorting_option)

    max_time = int(request.max_time)

    kwic_words = []
    start_time = timeit.default_timer()
    hits = db.query(request["q"], request["method"], request["arg"], **request.metadata)
    c = db.dbh.cursor()

    for hit in hits[index:]:
        word_id = ' '.join([str(i) for i in hit.philo_id])
        query = 'select rowid, philo_name, parent from words where philo_id="%s" limit 1' % word_id
        c.execute(query)
        results = c.fetchone()

        parent_sentence = results['parent']

        result_obj = {
            "left": "",
            "right": "",
            "index": index
        }

        left_rowid = results["rowid"] - 10
        right_rowid = results["rowid"] + 10

        c.execute('select philo_name, philo_id from words where rowid between ? and ?',
                  (left_rowid, results['rowid']-1))
        result_obj["left"] = []
        for i in c.fetchall():
            result_obj["left"].append(i['philo_name'].decode('utf-8'))
        result_obj["left"].reverse()
        result_obj["left"] = ' '.join(result_obj["left"])

        c.execute('select philo_name, philo_id from words where rowid between ? and ?',
                  (results['rowid']+1, right_rowid))
        result_obj["right"] = []
        for i in c.fetchall():
            result_obj["right"].append(i['philo_name'].decode('utf-8'))
        result_obj["right"] = ' '.join(result_obj["right"])

        metadata_fields = {}
        for metadata in metadata_to_extract:
            result_obj[metadata] = hit[metadata].lower()

        kwic_words.append(result_obj)

        index += 1

        elapsed = timeit.default_timer() - start_time
        if elapsed > max_time:  # avoid timeouts by splitting the query if more than 10 seconds has been spent in the loop
            break

    yield simplejson.dumps({"results": kwic_words, "hits_done": index})


if __name__ == "__main__":
    CGIHandler().run(get_neighboring_words)
