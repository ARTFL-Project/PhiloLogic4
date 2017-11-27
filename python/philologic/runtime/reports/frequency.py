#!/usr/bin env python
"""Frequency results for facets"""

import timeit

from philologic.runtime.link import make_absolute_query_link
from philologic.DB import DB


def frequency_results(request, config, sorted_results=False):
    """reads through a hitlist. looks up request.frequency_field in each hit, and builds up a list of
       unique values and their frequencies."""
    db = DB(config.db_path + '/data/')
    biblio_search = False
    if request.q == '' and request.no_q:
        biblio_search = True
        if request.no_metadata:
            hits = db.get_all(db.locals['default_object_level'], sort_order=["rowid"], raw_results=True)
        else:
            hits = db.query(sort_order=["rowid"], raw_results=True, **request.metadata)
    else:
        hits = db.query(request["q"], request["method"], request["arg"], raw_results=True, **request.metadata)

    if sorted_results:
        hits.finish()

    cursor = db.dbh.cursor()

    cursor.execute('select philo_id, %s from toms where %s is not null' % (request.frequency_field, request.frequency_field))
    metadata_dict = {}
    for i in cursor:
        philo_id, field = i
        philo_id = tuple(int(s) for s in philo_id.split() if int(s))
        metadata_dict[philo_id] = field

    counts = {}
    frequency_object = {}
    start_time = timeit.default_timer()
    last_hit_done = request.start

    obj_dict = {'doc': 1, 'div1': 2, 'div2': 3, 'div3': 4, 'para': 5, 'sent': 6, 'word': 7}
    metadata_type = db.locals["metadata_types"][request.frequency_field]
    try:
        object_level = obj_dict[metadata_type]
    except KeyError:
        # metadata_type == "div"
        pass

    try:
        for philo_id in hits[request.start:]:
            if not biblio_search:
                philo_id = tuple(list(philo_id[:6]) + [philo_id[7]])
            if metadata_type == "div":
                key = ""
                for div in ["div1", "div2", "div3"]:
                    if philo_id[:obj_dict[div]] in metadata_dict:
                        key = metadata_dict[philo_id[:obj_dict[div]]]
                while not key:
                    if philo_id[:4] in metadata_dict:
                        key = metadata_dict[philo_id[:4]]
                        break
                    if philo_id[:5] in metadata_dict:
                        key = metadata_dict[philo_id[:5]]
                        break
                    break
                if not key:
                    last_hit_done += 1
                    continue
            else:
                try:
                    key = metadata_dict[philo_id[:object_level]]
                except:
                    last_hit_done += 1
                    continue
            if key not in counts:
                counts[key] = {"count": 0, 'metadata': {request.frequency_field: key}}
                counts[key]["url"] = make_absolute_query_link(config,
                                                              request,
                                                              frequency_field="",
                                                              start="0",
                                                              end="0",
                                                              report=request.report,
                                                              script='',
                                                              **{request.frequency_field: '"%s"' % key})
                if not biblio_search:
                    query_metadata = dict([(k, v) for k, v in request.metadata.iteritems() if v])
                    import sys
                    print >> sys.stderr, "KEY", repr(key)
                    query_metadata[request.frequency_field] = '"%s"' % key
                    local_hits = db.query(**query_metadata)
                    counts[key]["total_word_count"] = local_hits.get_total_word_count()
            counts[key]["count"] += 1

            # avoid timeouts by splitting the query if more than
            # request.max_time (in seconds) has been spent in the loop
            elapsed = timeit.default_timer() - start_time
            last_hit_done += 1
            if elapsed > 5 and sorted_results is False:
                break

        frequency_object['results'] = counts
        frequency_object["hits_done"] = last_hit_done
        if last_hit_done == len(hits):
            new_metadata = dict([(k, v) for k, v in request.metadata.iteritems() if v])
            new_metadata[request.frequency_field] = '"NULL"'
            if request.q == '' and request.no_q:
                new_hits = db.query(sort_order=["rowid"], raw_results=True, **new_metadata)
            else:
                new_hits = db.query(request["q"], request["method"], request["arg"], raw_results=True, **new_metadata)
            new_hits.finish()
            if len(new_hits):
                null_url = make_absolute_query_link(config,
                                                    request,
                                                    frequency_field="",
                                                    start="0",
                                                    end="0",
                                                    report=request.report,
                                                    script='',
                                                    **{request.frequency_field: '"NULL"'})
                local_hits = db.query(**new_metadata)
                if not biblio_search:
                    frequency_object["results"]["NULL"] = {"count": len(new_hits),
                                                           "url": null_url,
                                                           "metadata": {request.frequency_field: '"NULL"'},
                                                           "total_word_count": local_hits.get_total_word_count()}
                else:
                    frequency_object["results"]["NULL"] = {"count": len(new_hits),
                                                           "url": null_url,
                                                           "metadata": {request.frequency_field: '"NULL"'}}
            frequency_object['more_results'] = False
        else:
            frequency_object['more_results'] = True
    except IndexError:
        frequency_object['results'] = {}
        frequency_object['more_results'] = False
    frequency_object['results_length'] = len(hits)
    frequency_object['query'] = dict([i for i in request])

    if sorted_results:
        frequency_object["results"] = sorted(frequency_object['results'].iteritems(),
                                             key=lambda x: x[1]['count'],
                                             reverse=True)

    return frequency_object
