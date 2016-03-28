#!/usr/bin/env python

import sys
sys.path.append('..')
from functions.wsgi_handler import WSGIHandler
from philologic.DB import DB
from wsgiref.handlers import CGIHandler
import reports as r
import functions as f
import ujson as json


def get_frequency(environ, start_response):
    """reads through a hitlist. looks up q.frequency_field in each hit, and builds up a list of
       unique values and their frequencies."""
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),
               ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    if request.q == '' and request.no_q:
        if request.no_metadata:
            hits = db.get_all(db.locals['default_object_level'])
        else:
            hits = db.query(**request.metadata)
    else:
        hits = db.query(request["q"], request["method"], request["arg"],
                        **request.metadata)
    results = r.generate_frequency(hits, request, db, config)
    yield json.dumps(results)



    # field_list = eval(json.loads(request.frequency_field))
    # table = {}
    # frequency_object = {}
    #
    # metadata_hits = db.query(**request.metadata)
    # for metadata_hit in metadata_hits:
    #     query_fields = dict(request.metadata)
    #     key = []
    #     for field in field_list:
    #         value = metadata_hit[field]
    #         if not value:
    #             # print >> sys.stderr, "NULL FOUND", hit.head, hit.philo_id, hit[field]
    #             # NULL is a magic value for queries, don't change it recklessly.
    #             value = "NULL"
    #         query_fields[field] = value.encode('utf-8', 'ignore')
    #         key.append((field, value))
    #     local_hits = db.query(request["q"], request["method"], request["arg"],
    #                          **query_fields)
    #     local_hits.finish()
    #     count = len(local_hits)
    #
    #     if count:
    #         # Make a distinct copy for each key in case we modify it below
    #         metadata = dict(request.metadata)
    #
    #         first_metatada_key, first_metadata_value = key[0]
    #         label = first_metadata_value
    #         metadata[first_metatada_key] = first_metadata_value.encode('utf-8', 'ignore')
    #         append_to_label = []
    #         for metadata_key, metadata_value in key[1:]:
    #             if metadata_value == "NULL":
    #                 # replace NULL with '[None]', 'N.A.', 'Untitled', etc.
    #                 metadata[metadata_key] = "NULL"
    #             else:
    #                 # we want to run exact queries on defined values.
    #                 metadata[metadata_key] = metadata_value.encode('utf-8', 'ignore')
    #                 append_to_label.append(metadata_value)
    #         # Add parentheses to other value, as they are secondary
    #         if append_to_label:
    #             label = label + ' (' + ', '.join(append_to_label) + ')'
    #
    #         # Quote metadata to force exact matches on metadata
    #         for m in metadata:
    #             if m not in request.metadata:  # skip metadata already in original query: this could be a glob search
    #                 if metadata[m] and m != "date" and metadata[m] != "NULL":
    #                     if not metadata[m].startswith('"'):
    #                         metadata[m] = '"%s"' % metadata[m]
    #         # Now build the url from q.
    #         url = f.link.make_absolute_query_link(config,
    #                                               request,
    #                                               frequency_field="",
    #                                               start="0",
    #                                               end="0",
    #                                               report=request.report,
    #                                               script='',
    #                                               **metadata)
    #         table[label] = {'count': count, 'url': url, 'metadata': metadata}
    #
    # frequency_object['results'] = table
    # frequency_object['more_results'] = False
    # frequency_object['results_length'] = len("results")
    # frequency_object['query'] = dict([i for i in request])
    #
    # yield json.dumps(frequency_object)


if __name__ == "__main__":
    CGIHandler().run(get_frequency)
