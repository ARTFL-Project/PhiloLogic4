#!/usr/bin env python
from __future__ import division

import sys
import timeit
from ast import literal_eval as eval
from collections import defaultdict

sys.path.append('..')
import functions as f

try:
    import ujson as json
except ImportError:
    import json



def generate_frequency(results, q, db, config):
    """reads through a hitlist. looks up q.frequency_field in each hit, and builds up a list of
       unique values and their frequencies."""

    field_list = eval(json.loads(q.frequency_field))

    counts = defaultdict(int)
    frequency_object = {}
    start_time = timeit.default_timer()
    last_hit_done = q.start

    try:
        for hit in results[q.start:]:
            key = tuple((field, hit[field]) for field in field_list)
            counts[key] += 1

            # avoid timeouts by splitting the query if more than q.max_time (in seconds) has been spent in the loop
            elapsed = timeit.default_timer() - start_time
            last_hit_done += 1
            if elapsed > 5:
                break

        table = {}
        for key, count in counts.iteritems():
            # for each item in the table, we modify the query params to
            # generate a link url.
            # Make a distinct copy for each key in case we modify it below
            metadata = dict(q.metadata)

            # Build a label starting with the first value as the main value
            first_metatada_key, first_metadata_value = key[0] or "NULL"
            label = first_metadata_value
            metadata[first_metatada_key] = first_metadata_value.encode('utf-8', 'ignore')
            append_to_label = []
            for metadata_key, metadata_value in key[1:]:
                if not metadata_value:
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
        frequency_object["hits_done"] = last_hit_done
        if last_hit_done == len(results):
            frequency_object['more_results'] = False
        else:
            frequency_object['more_results'] = True
    except IndexError:
        frequency_object['results'] = {}
        frequency_object['more_results'] = False
    frequency_object['results_length'] = len(results)
    frequency_object['query'] = dict([i for i in q])

    return frequency_object
