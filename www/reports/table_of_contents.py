#!/usr/bin/env python

import sys
sys.path.append('..')
import functions as f
from philologic.DB import DB
from functions.wsgi_handler import WSGIHandler
from wsgiref.handlers import CGIHandler
from philologic import HitWrapper
from concordance import citation_links
from bibliography import biblio_citation
try:
    import ujson as json
except ImportError:
    print >> sys.stderr, "Import Error, please install ujson for better performance"
    import json

philo_types = set(['div1', 'div2', 'div3'])
philo_slices = {"doc": 1, "div1": 2, "div2": 3, "div3": 4, "para": 5}

def table_of_contents(environ,start_response):
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    try:
        obj = db[request.philo_id]
    except ValueError:
        philo_id = ' '.join(request.path_components[:-1])
        obj = db[philo_id]
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response('200 OK',headers)
    toc_object = json.dumps(generate_toc_object(obj, db, request, config))
    yield toc_object

def nav_query(obj,db):
    conn = db.dbh
    c = conn.cursor()
    doc_id =  int(obj.philo_id[0])
    next_doc_id = doc_id + 1
    # find the starting rowid for this doc
    c.execute('select rowid from toms where philo_id="%d 0 0 0 0 0 0"' % doc_id)
    start_rowid = c.fetchone()[0]
    # find the starting rowid for the next doc
    c.execute('select rowid from toms where philo_id="%d 0 0 0 0 0 0"' % next_doc_id)
    try:
        end_rowid = c.fetchone()[0]
    except TypeError: # if this is the last doc, just get the last rowid in the table.
        c.execute('select max(rowid) from toms;')
        end_rowid = c.fetchone()[0]

    # use start_rowid and end_rowid to fetch every div in the document.
    c.execute("select * from toms where rowid >= ? and rowid <=? and philo_type>='div' and philo_type<='div3'", (start_rowid, end_rowid))
    for o in c.fetchall():
        id = [int(n) for n in o["philo_id"].split(" ")]
        i = HitWrapper.ObjectWrapper(id,db,row=o)
        yield i

def generate_toc_object(obj, db, q, config):
    """This function fetches all philo_ids for div elements within a doc"""
    toms_object = nav_query(obj, db)
    text_hierarchy = []
    for i in toms_object:
        if i['philo_name'] == '__philo_virtual' and i["philo_type"] != "div1":
            continue
        elif i['word_count'] == 0:
            continue
        else:
            philo_id = i['philo_id']
            philo_type = i['philo_type']
            display_name = ""
            if i['philo_name'] == "front":
                display_name = "Front Matter"
            elif i['philo_name'] == "note":
                continue
            else:
                display_name = i['head']
                if display_name:
                    display_name = display_name.strip()
                if not display_name:
                    if i["type"] and i["n"]:
                        display_name = i['type'] + " " + i["n"]                       
                    else:
                        display_name = i["head"] or i['type'] or i['philo_name'] or i['philo_type']
                        if display_name == "__philo_virtual":
                            display_name = i['philo_type']
            display_name = display_name[0].upper() + display_name[1:]
            link = f.make_absolute_object_link(config, philo_id.split()[:philo_slices[philo_type]])
            philo_id = ' '.join(philo_id.split()[:philo_slices[philo_type]])
            toc_element = {"philo_id": philo_id, "philo_type": philo_type, "label": display_name, "href": link}
            text_hierarchy.append(toc_element)
    metadata_fields = {}
    for metadata in db.locals['metadata_fields']:
        if db.locals['metadata_types'][metadata] == "doc":
            metadata_fields[metadata] = obj[metadata]
    citation_hrefs = citation_links(db, config, obj)
    citation = biblio_citation(obj, citation_hrefs)
    toc_object = {"query": dict([i for i in q]), "philo_id": obj.philo_id, "toc": text_hierarchy, "metadata_fields": metadata_fields,
                  "citation": citation}
    return toc_object

if __name__ == "__main__":
    CGIHandler().run(table_of_contents)
