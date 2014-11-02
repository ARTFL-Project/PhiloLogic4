#!/usr/bin env python
from __future__ import division
import sys
sys.path.append('..')
import functions as f
from functions.wsgi_handler import wsgi_response
from render_template import render_template
from collections import defaultdict
from math import log10
from ast import literal_eval as eval
import json

object_types = set(["doc", "div1", "div2", "div3", "para", "sent", "word"])

def frequency(environ,start_response):
    db, dbname, path_components, q = wsgi_response(environ,start_response)
    hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
    # if we have a json report, directly dump the table in a json wrapper.
    # if you want to change the URL value of a key, do it in generate_frequency() below.
    field, counts = generate_frequency(hits,q,db)

    l = len(counts)
    wrapper = {"length":l,"result":[],"field":field}
    for label, i in sorted(counts.iteritems(), key=lambda x: x[1]['count'], reverse=True):
        table_row = {"label":label,"count":i['count'],"url":i['url']}
        wrapper["result"].append(table_row)
    return json.dumps(wrapper,indent=1)

def generate_frequency(results, q, db):
    """reads through a hitlist. looks up q["field"] in each hit, and builds up a list of 
       unique values and their frequencies."""
    field = eval(q['field']).items()[0][1]
    
    if isinstance(field, str):
        field = [field]
    
    field_object = []
    for i in field:
        ## Testing for a possible object depth attribute such as div1.head or para.who and
        ## apply the corresponding depth for the SQL query
        depth = ''
        if i.split('.')[0] in object_types and i.split('.')[-1] in db.locals['metadata_fields']:
            depth = i.split('.')[0]
            i = i.split('.')[-1]
        field_object.append((i, depth))
     
    counts = defaultdict(int)
    for hit in results[q['interval_start']:q['interval_end']]:
        key = generate_key(hit, field_object, db)
        counts[key] += 1

    table = {}
    for key,count in counts.iteritems():
        # for each item in the table, we modify the query params to generate a link url.
        key = eval(key)      
        metadata = dict(q['metadata']) ## Make a distinct copy for each key in case we may modify it below
        
        ## Build a label starting with the first value as the main value
        label = key[0]['value']
        metadata[key[0]['field']] = key[0]['value'].encode('utf-8', 'ignore')
        append_to_label= []
        for k in key[1:]:
            if k['value'] == "NULL":
                metadata[k['field']] = "NULL" # replace NULL with '[None]', 'N.A.', 'Untitled', etc.
            else:
                metadata[k['field']] = k['value'].encode('utf-8', 'ignore') # we want to run exact queries on defined values.
                append_to_label.append(k['value'])
        ## Add parentheses to other value, as they are secondary
        if append_to_label:
            label = label + ' (' + ', '.join(append_to_label) + ')'
        
        # Now build the url from q.
        url = f.link.make_query_link(q["q"],q["method"],q["arg"],q["report"],**metadata)
    
        table[label] = {'count': count, 'url': url}

    return field, table

def generate_key(hit, field_object, db):
    key = []
    for field, depth in field_object:
        k = {"field": field}
        if field in db.locals['metadata_types'] and not depth:
            depth = db.locals['metadata_types'][field]
        if depth:
            if depth == "div":
                for d in ["div3", "div2", "div1"]:
                    k['value'] = hit[d][field]
                    if k['value']:
                        break
            else:
                k['value'] = hit[depth][field]
        else:
            k['value'] = hit[field]
        if not k['value']:
            k['value'] = "NULL" # NULL is a magic value for queries, don't change it recklessly.
        key.append(k)
    key = repr(key)
    return key
    
def relative_frequency(field, label, count, db, doc=False):
    c = db.dbh.cursor()
    if label == 'NULL':
        label = ''
    if doc:
        query = 'select sum(word_count) from toms where %=? and title=?' % field
        c.execute(query, (label, doc))
    else:
        query = 'select sum(word_count) from toms where %s=?' % field
        c.execute(query, (label,))
    result = count / c.fetchone()[0] * 10000
    return "%.2f" % round(result, 3)

def tf_idf(field, label, count, db, idf, doc=False):
    c = db.dbh.cursor()
    if label == 'NULL':
        label = ''
    if doc:
        query = 'select sum(word_count) from toms where %s=? and title=?' % field
        c.execute(query, (label, doc))
    else:
        query = 'select sum(word_count) from toms where %s=?' % field
        c.execute(query, (label,))
    result = count / c.fetchone()[0] * idf *10000
    return "%.2f" % round(result, 3)

