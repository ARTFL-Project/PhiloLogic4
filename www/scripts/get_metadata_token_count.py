#!/usr/bin/env python

from __future__ import division
import timeit
import sys
sys.path.append('..')
from copy import deepcopy
from philologic.DB import DB
from philologic.MetadataQuery import corpus_cmp, expand_grouped_query, make_grouped_sql_clause, str_to_hit
from philologic.QuerySyntax import parse_query, group_terms
from wsgiref.handlers import CGIHandler
import functions as f
try:
    import ujson as json
except ImportError:
    import json


def parse_metadata(db, metadata):
    for key, value in metadata.items():
        if isinstance(value, str):
            if value == "":
                pass
            else:
                value = [value]
                metadata[key] = value
    metadata_dicts = [{} for level in db.locals["metadata_hierarchy"]]
    for k, v in metadata.items():
        for i, params in enumerate(db.locals["metadata_hierarchy"]):
            if v and (k in params):
                metadata_dicts[i][k] = v
                if k in db.locals["metadata_types"]:
                    this_type = db.locals["metadata_types"][k]
                    if this_type == "div":
                        metadata_dicts[i]["philo_type"] = [
                            '"div"|"div1"|"div2"|"div3"']
                    else:
                        metadata_dicts[i]["philo_type"] = [
                            '"%s"' % db.locals["metadata_types"][k]]
    metadata_dicts = [d for d in metadata_dicts if d]
    if "philo_id" in metadata:
        if metadata_dicts:
            metadata_dicts[-1]["philo_id"] = metadata["philo_id"]
        else:
            metadata_dicts.append({"philo_id": metadata["philo_id"]})
    return metadata_dicts


def query_recursive(db, param_dict, parent):
    r = query_lowlevel(db, param_dict)
    if parent:
        try:
            outer_hit = next(parent)
        except StopIteration:
            return
        for inner_hit in r:
            while corpus_cmp(str_to_hit(outer_hit["philo_id"]), str_to_hit(inner_hit["philo_id"])) < 0:
                try:
                    outer_hit = next(parent)
                except StopIteration:
                    return
            if corpus_cmp(str_to_hit(outer_hit["philo_id"]), str_to_hit(inner_hit["philo_id"])) > 0:
                continue
            else:
                yield inner_hit
    else:
        for row in r:
            yield row


def query_lowlevel(db, param_dict):
    vars = []
    clauses = []
    # if column = _philo_id I can do a special query here
    for column, values in param_dict.items():
        norm_path = db.path + "/frequencies/normalized_" + column + "_frequencies"
        for v in values:
            try:
                v = v.decode('utf-8')
            except:
                pass
            parsed = parse_query(v)
            if db.locals['debug']:
                print >> sys.stderr, "METADATA_TOKENS:", parsed
            grouped = group_terms(parsed)
            if db.locals['debug']:
                print >> sys.stderr, "METADATA_SYNTAX:", grouped
            expanded = expand_grouped_query(grouped, norm_path)
            if db.locals['debug']:
                print >> sys.stderr, "METADATA_SYNTAX:", expanded
            sql_clause = make_grouped_sql_clause(expanded, column)
            if db.locals['debug']:
                print >> sys.stderr, "SQL_SYNTAX:", sql_clause
            clauses.append(sql_clause)
    if clauses:
        query = "SELECT word_count, philo_id FROM toms WHERE " + \
            " AND ".join("(%s)" % c for c in clauses) + ";"
    else:
        query = "SELECT word_count, philo_id FROM toms;"

    if db.locals['debug']:
        print >> sys.stderr, "INNER QUERY: ", "%s %% %s" % (query, vars)

    results = db.dbh.execute(query, vars)
    return results


def get_total_count(db, param_dicts):
    param_dicts = parse_metadata(db, param_dicts)
    prev = None
    for d in param_dicts:
        query = query_recursive(db, d, prev)
        prev = query
    total_count = 0
    for corpus_obj in query:
        total_count += int(corpus_obj['word_count'])
    return total_count


def get_metadata_token_count(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),
               ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')

    input_object = json.loads(environ['wsgi.input'].read())
    frequencies = input_object['results']
    hits_done = input_object['hits_done']
    start_time = timeit.default_timer()
    count = 0
    sorted_frequencies = sorted(frequencies.iteritems(), key=lambda x: x[0])

    start_hits_done = deepcopy(hits_done)

    for label, m in sorted_frequencies[start_hits_done:]:
        query_metadata = {}
        for metadata in m['metadata']:
            if m['metadata'][metadata] and m['metadata'][metadata] != "NULL":
                if metadata == 'date' and '-' in m['metadata'][metadata]:
                    query_metadata[metadata] = m[
                        'metadata'][metadata].encode('utf-8')
                else:
                    query_metadata[metadata] = m[
                        'metadata'][metadata].encode('utf-8')
            elif m['metadata'][metadata] == "NULL":
                query_metadata[metadata] = "NULL"
        total_count = get_total_count(db, query_metadata)
        try:
            frequencies[label]['count'] = round(
                m['count'] / total_count * 10000, 3)
        except:
            count += 1
            frequencies[label]['count'] = 0
        frequencies[label]['total_count'] = total_count
        hits_done += 1
        elapsed = timeit.default_timer() - start_time
        if elapsed > 5:  # avoid timeouts by splitting the query if more than 10 seconds has been spent in the loop
            break

    if len(sorted_frequencies) > hits_done:
        more_results = True
    else:
        more_results = False

    yield json.dumps({"frequencies": dict(sorted_frequencies[start_hits_done:hits_done]),
                      "more_results": more_results,
                      "hits_done": hits_done})


if __name__ == "__main__":
    CGIHandler().run(get_metadata_token_count)
