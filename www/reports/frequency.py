#!/usr/bin env python
from __future__ import division
import sys
sys.path.append('..')
import functions as f
from functions.wsgi_handler import wsgi_response
from render_template import render_template
from collections import defaultdict
import json
import re

def frequency(environ,start_response):
    db, dbname, path_components, q = wsgi_response(environ,start_response)
    hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
    if q["format"] == "json":
        # if we have a json report, directly dump the table in a json wrapper.
        # if you want to change the URL value of a key, do it in generate_frequency() below.
        field, counts = generate_frequency(hits,q,db)

        l = len(counts)
        wrapper = {"length":l,"result":[],"field":field}
        for label,count,url in counts:
            table_row = {"label":label,"count":count,"url":url}
            wrapper["result"].append(table_row)
        return json.dumps(wrapper,indent=1)
        
    else:
        return render_template(results=hits,db=db,dbname=dbname,q=q,generate_frequency=generate_frequency,f=f, template_name='frequency.mako')

def generate_frequency(results, q, db):
    """reads through a hitlist. looks up q["field"] in each hit, and builds up a list of 
       unique values and their frequencies."""
    field = q["field"]
    if field == None:
        field = 'title'
    counts = defaultdict(int)
    key_disp = {}
    for n in results:
        key = n[field] or "NULL" # NULL is a magic value for queries, don't change it recklessly.
        if field in db.locals["normalized_fields"]:
            disp_field = field.replace("_norm","")
            disp_key = n[disp_field]
            key_disp[key] = disp_key
        counts[key] += 1

    if q['rate'] == 'relative':
        conn = db.dbh ## make this more accessible 
        c = conn.cursor()
        for key, count in counts.iteritems():
            counts[key] = relative_frequency(field, key, count, db)

    table = []
    for k,v in sorted(counts.iteritems(),key=lambda x: x[1], reverse=True)[:100]:
        # for each item in the table, we modify the query params to generate a link url.
        if k == "NULL":
            q["metadata"][field] = k # NULL is a magic boolean keyword, not a string value.
        else:
            q["metadata"][field] = '"%s"' % k.encode('utf-8', 'ignore') # we want to do exact queries on defined values.
        # Now build the url from q.
        url = f.link.make_query_link(q["q"],q["method"],q["arg"],**q["metadata"])     

        # Contruct the label for the item.        
        if k in key_disp:
            label = key_disp[k]
        else:
            label = k
        
        # We can also modify the count.
        if q['rate'] == 'relative':
            count = relative_frequency(field,key,v,db)
        else:
            count = v
            
        table.append( (label,v,url) )

    return field, table
    
def relative_frequency(field, label, count, db):
    c = db.dbh.cursor()
    query = '''select sum(word_count) from toms where %s="%s"''' % (field, label)
    c.execute(query)
    return count / c.fetchone()[0] * 10000
