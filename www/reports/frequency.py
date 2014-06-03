#!/usr/bin env python
from __future__ import division
import sys
sys.path.append('..')
import functions as f
from functions.wsgi_handler import wsgi_response
from render_template import render_template
from collections import defaultdict
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
    field = q["field"]
    depth = ''
    ## Testing for a possible object depth attribute such as div1.head or para.who and
    ## apply the corresponding depth for the SQL query
    if field.split('.')[0] in object_types and field.split('.')[-1] in db.locals['metadata_fields']:
        depth = field.split('.')[0]
        field = field.split('.')[-1]
    counts = defaultdict(int)
    for n in results[q['interval_start']:q['interval_end']]:
        ## This is to minimize the number of SQL queries
        if field in db.locals['metadata_types'] and not depth:
            depth = db.locals['metadata_types'][field]
        if depth:
            if depth == "div":
                for d in ["div3", "div2", "div1"]:
                    key = n[d][field]
                    if key:
                        break
            else:
                key = n[depth][field]
        else:
            key = n[field]
        if not key:
            key = "NULL" # NULL is a magic value for queries, don't change it recklessly.
        counts[key] += 1

    if q['rate'] == 'relative':
        for key, count in counts.iteritems():
            counts[key] = relative_frequency(field, key, count, db)

    table = {}
    for k,v in counts.iteritems():
        # for each item in the table, we modify the query params to generate a link url.
        if k == "NULL":
            q["metadata"][field] = k # NULL is a magic boolean keyword, not a string value.
        else:
            q["metadata"][field] = '"%s"' % k.encode('utf-8', 'ignore') # we want to do exact queries on defined values.
        # Now build the url from q.
        url = f.link.make_query_link(q["q"],q["method"],q["arg"],q["report"],**q["metadata"])     

        # Contruct the label for the item.
        # This is the place to modify the displayed label of frequency table item.
        label = k #for example, replace NULL with '[None]', 'N.A.', 'Untitled', etc.
            
        table[label] = {'count': v, 'url': url}

    return field, table
    
def relative_frequency(field, label, count, db):
    c = db.dbh.cursor()
    if label == 'NULL':
        label = ''
    query = 'select sum(word_count) from toms where %s=?' % field
    c.execute(query, (label,))
    result = count / c.fetchone()[0] * 10000
    return "%.2f" % round(result, 3)
