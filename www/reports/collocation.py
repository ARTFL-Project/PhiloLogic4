#!/usr/bin/env python

from __future__ import division
import sys
sys.path.append('..')
import functions as f
try:
    import ujson as json
except ImportError:
    import json
import timeit
from collections import defaultdict
from math import log10 as log
from philologic.DB import DB
from wsgiref.handlers import CGIHandler
from functions.wsgi_handler import WSGIHandler
from philologic.Query import get_expanded_query


def collocation(environ, start_response):
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    headers = [('Content-type', 'application/json; charset=UTF-8'),
               ("Access-Control-Allow-Origin", "*")]
    start_response('200 OK', headers)
    if request["collocate_distance"]:
        hits = db.query(request["q"], "proxy", int(request['collocate_distance']), **request.metadata)
    else:
        hits = db.query(request["q"], "cooc", request["arg"], **request.metadata)
    hits.finish()
    collocation_object = fetch_collocation(hits, request, db, config)
    yield json.dumps(collocation_object)


def fetch_collocation(hits, request, db, config):
    collocation_object = {"query": dict([i for i in request])}

    length = config['concordance_length']
    try:
        collocate_distance = int(request['collocate_distance'])
    except ValueError:  # Getting an empty string since the keyword is not specificed in the URL
        collocate_distance = None

    if request.colloc_filter_choice == "nofilter":
        filter_list = []
    else:
        filter_list = build_filter_list(request, config)
    collocation_object['filter_list'] = filter_list
    filter_list = set(filter_list)

    # Build list of search terms to filter out
    query_words = []
    for group in get_expanded_query(hits):
        for word in group:
            word = word.replace('"', '')
            query_words.append(word)
    query_words = set(query_words)
    filter_list = filter_list.union(query_words)

    stored_sentence_id = None
    stored_sentence_counts = defaultdict(int)
    sentence_hit_count = 1
    hits_done = request.start or 0
    max_time = request.max_time or 10
    all_collocates = defaultdict(lambda: {'count': 0})
    cursor = db.dbh.cursor()
    start_time = timeit.default_timer()
    try:
        for hit in hits[hits_done:]:
            word_id = ' '.join([str(i) for i in hit.philo_id])
            query = """select philo_name, parent, rowid from words where philo_id='%s'""" % word_id
            cursor.execute(query)
            result = cursor.fetchone()
            parent = result['parent']
            rowid = int(result['rowid'])
            if parent != stored_sentence_id:
                sentence_hit_count = 1
                stored_sentence_id = parent
                stored_sentence_counts = defaultdict(int)
                if collocate_distance:
                    begin_rowid = rowid - collocate_distance
                    if begin_rowid < 0:
                        begin_rowid = 0
                    end_rowid = rowid + collocate_distance
                    row_query = """select philo_name from words where parent='%s' and rowid between %d and %d""" % (
                        parent, begin_rowid, end_rowid)
                else:
                    row_query = """select philo_name from words where parent='%s'""" % (
                        parent, )
                cursor.execute(row_query)
                for i in cursor.fetchall():
                    stored_sentence_counts[i['philo_name']] += 1
            else:
                sentence_hit_count += 1
            for word in stored_sentence_counts:
                if word in filter_list or stored_sentence_counts[word] < sentence_hit_count:
                    continue
                all_collocates[word]['count'] += 1
            hits_done += 1
            elapsed = timeit.default_timer() - start_time
            # avoid timeouts by splitting the query if more than q.max_time (in
            # seconds) has been spent in the loop
            if elapsed > int(max_time):
                break
    except IndexError:
        collocation['hits_done'] = len(hits)

    log_collocates = {}
    # cursor.execute("""select count(*) from words where philo_name='%s'""" % request.q)
    # total_word_count = cursor.fetchone()[0]
    # for i in all_collocates:
    #     all_collocates[i]["count"] = log_likelihood(total_word_count, all_collocates[i]["count"], i, cursor)


    collocation_object['collocates'] = all_collocates

    collocation_object["results_length"] = len(hits)
    if hits_done < collocation_object["results_length"]:
        collocation_object['more_results'] = True
        collocation_object['hits_done'] = hits_done
    else:
        collocation_object['more_results'] = False
        collocation_object['hits_done'] = collocation_object["results_length"]

    return collocation_object


def build_filter_list(q, config):
    ## set up filtering with stopwords or most frequent terms ##
    if config.stopwords and q.colloc_filter_choice == "stopwords":
        filter_file = open(config.db_path + '/data/' + config.stopwords)
        filter_num = float("inf")
    else:
        filter_file = open(
            config.db_path + '/data/frequencies/word_frequencies')
        if q.filter_frequency:
            filter_num = int(q.filter_frequency)
        else:
            filter_num = 100  # default value in case it's not defined
    filter_list = [q['q']]
    for line_count, line in enumerate(filter_file):
        if line_count == filter_num:
            break
        try:
            word = line.split()[0]
        except IndexError:
            continue
        filter_list.append(word)
    return filter_list


def log_likelihood(total_word_count, collocate_count, collocate, cursor):
    query = """select count(*) from words where philo_name='%s'""" % collocate
    cursor.execute(query)
    total_collocate_count = cursor.fetchone()[0]
    a = collocate_count
    b = total_word_count - a or 1
    c = total_collocate_count - a or 1
    cursor.execute('select rowid from words order by rowid desc limit 1')
    d = cursor.fetchone()[0] - total_collocate_count - total_word_count
    print >> sys.stderr, "HEYYYYY", a, b, c, d
    # score = 2*( a*log(a) + b*log(b) + c*log(c))
    score = 2*( a*log(a) + b*log(b) + c*log(c) + d*log(d) - (a+b)*log(a+b) - (a+c)*log(a+c) - (b+d)*log(b+d) - (c+d)*log(c+d) + (a+b+c+d)*log(a+b+c+d))
    return score


def mutual_information(total_word_count, collocate_count, collocate, cursor):
    if collocate_count < 5:
        return 0
    query = """select count(*) from words where philo_name='%s'""" % collocate
    cursor.execute(query)
    total_collocate_count = cursor.fetchone()[0]
    cursor.execute('select rowid from words order by rowid desc limit 1')
    total_words = cursor.fetchone()[0] + 1
    span = 20
    print >> sys.stderr, "hEYYYYY", collocate_count, total_words, total_word_count, total_collocate_count
    score = log((collocate_count * total_words) / (total_word_count * total_collocate_count * span)) / log(2)
    # score = collocate_count / (total_word_count * span / (collocate_count / total_words))
    return score



if __name__ == "__main__":
    CGIHandler().run(collocation)
