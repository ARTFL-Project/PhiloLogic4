#!/usr/bin env python
from __future__ import division
import sys
sys.path.append('..')
import functions as f
from collections import defaultdict
from ast import literal_eval as eval
try:
    import ujson as json
except ImportError:
    import json


def generate_frequency(results, q, db, config):
    """reads through a hitlist. looks up q.frequency_field in each hit, and builds up a list of
       unique values and their frequencies."""

    field_list = eval(json.loads(q.frequency_field))

    # Override default value of q.end for first batch of results
    if q.end == 25:
        q.end = 5000

    counts = defaultdict(int)
    frequency_object = {}

    try:
        for hit in results[q.start:q.end]:
            key = []
            for field in field_list:
                value = hit[field]
                if not value:
                    # print >> sys.stderr, "NULL FOUND", hit.head, hit.philo_id, hit[field]
                    # NULL is a magic value for queries, don't change it recklessly.
                    value = "NULL"
                k = (field, value)
                key.append(k)
            key = tuple(key)
            counts[key] += 1

        table = {}
        for key, count in counts.iteritems():
            # for each item in the table, we modify the query params to
            # generate a link url.
            # Make a distinct copy for each key in case we modify it below
            metadata = dict(q.metadata)

            # Build a label starting with the first value as the main value
            first_metatada_key, first_metadata_value = key[0]
            label = first_metadata_value
            metadata[first_metatada_key] = first_metadata_value.encode('utf-8', 'ignore')
            append_to_label = []
            for metadata_key, metadata_value in key[1:]:
                if metadata_value == "NULL":
                    # replace NULL with '[None]', 'N.A.', 'Untitled', etc.
                    metadata[metadata_key] = "NULL"
                else:
                    # we want to run exact queries on defined values.
                    metadata[metadata_key] = metadata_value.encode('utf-8', 'ignore')
                    append_to_label.append(metadata_value)
            # Add parentheses to other value, as they are secondary
            if append_to_label:
                label = label + ' (' + ', '.join(append_to_label) + ')'

            # Quote metadata to force exact matches on metadata
            for m in metadata:
                if m not in q.metadata:  # skip metadata already in original query: this could be a glob search
                    if metadata[m] and m != "date" and metadata[m] != "NULL":
                        if not metadata[m].startswith('"'):
                            metadata[m] = '"%s"' % metadata[m]
            # Now build the url from q.
            url = f.link.make_absolute_query_link(config,
                                                  q,
                                                  frequency_field="",
                                                  start="0",
                                                  end="0",
                                                  report=q.report,
                                                  script='',
                                                  **metadata)
            table[label] = {'count': count, 'url': url, 'metadata': metadata}
        frequency_object['results'] = table
        frequency_object['more_results'] = True
    except IndexError:
        frequency_object['results'] = {}
        frequency_object['more_results'] = False
    frequency_object['results_length'] = len(results)
    frequency_object['query'] = dict([i for i in q])

    return frequency_object
