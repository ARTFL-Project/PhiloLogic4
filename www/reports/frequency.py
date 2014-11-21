#!/usr/bin env python
from __future__ import division
import sys
sys.path.append('..')
import functions as f
from functions.wsgi_handler import WSGIHandler
from collections import defaultdict
import json

def generate_frequency(results, q, db, config):
    """reads through a hitlist. looks up q.frequency_field in each hit, and builds up a list of 
       unique values and their frequencies."""
    field = ''
    for facet in config.facets:
        key, value = facet.items()[0]
        if key == q.frequency_field:
            field = value
            break
    
    if isinstance(field, str):
        field = [field]
     
    counts = defaultdict(int)
    for hit in results[q.interval_start:q.interval_end]:
        key = generate_key(hit, field, db)
        counts[key] += 1

    table = {}
    for key,count in counts.iteritems():
        # for each item in the table, we modify the query params to generate a link url.      
        metadata = dict(q.metadata) ## Make a distinct copy for each key in case we may modify it below
        
        ## Build a label starting with the first value as the main value
        first_metatada_key, first_metadata_value = key[0]
        label = first_metadata_value
        metadata[first_metatada_key] = first_metadata_value.encode('utf-8', 'ignore')
        append_to_label= []
        for metadata_key, metadata_value in key[1:]:
            if metadata_value == "NULL":
                metadata[metadata_key] = "NULL" # replace NULL with '[None]', 'N.A.', 'Untitled', etc.
            else:
                metadata[metadata_key] = metadata_value.encode('utf-8', 'ignore') # we want to run exact queries on defined values.
                append_to_label.append(metadata_value)
        ## Add parentheses to other value, as they are secondary
        if append_to_label:
            label = label + ' (' + ', '.join(append_to_label) + ')'
        
        # Now build the url from q.
        url = f.link.make_query_link(q["q"],q["method"],q["arg"],q["report"],**metadata)
    
        table[label] = {'count': count, 'url': url}

    return field, table

def generate_key(hit, field_list, db):
    key = []
    for field in field_list:
        value = hit[field]
        if not value:
            value = "NULL" # NULL is a magic value for queries, don't change it recklessly.
        k = (field, value)
        key.append(k)
    key = tuple(key)
    return key