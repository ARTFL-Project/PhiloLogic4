#!/usr/bin/env python

import re
import sys
import unicodedata
from wsgiref.handlers import CGIHandler

from philologic.DB import DB

sys.path.append('..')
import functions as f
from functions.wsgi_handler import WSGIHandler

try:
    import ujson as json
except ImportError:
    import json

object_depth = {"doc": 1, "div1": 2, "div2": 3, "div3": 4, "para": 5}


def landing_page_content(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'), ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    if request.is_range == 'true':
        if type(request.query) == str:
            request_range = request.query.decode("utf8")
        request_range = request_range.lower().split('-')
        results = group_by_range(request_range, request, db)
    else:
        results = group_by_metadata(request, db)
    yield results


def date_range(query_range):
    is_date = False
    try:
        int(query_range[0])
        int(query_range[1])
        is_date = True
    except ValueError:
        pass
    return is_date


def group_by_range(request_range, request, db):
    is_date = date_range(request_range)
    if is_date:
        content_type = "date"
        query_range = set(range(int(request_range[0]), int(request_range[1])))
    else:
        content_type = request.metadata_display
        query_range = set(range(ord(request_range[0]), ord(request_range[1]) + 1))  # Ordinal avoids unicode issues...
    c = db.dbh.cursor()
    c.execute('select *, count(*) as count from toms where philo_type="doc" group by %s' % request.group_by_field)
    content = []
    metadata_displayed = ""
    for doc in c.fetchall():
        normalized_test_value = ''
        if doc[request.group_by_field] is None:
            continue
        if is_date:
            try:
                initial = int(doc[request.group_by_field])
                test_value = initial
            except:
                continue
        else:
            initial_letter = doc[request.group_by_field].decode('utf-8')[0].lower()
            test_value = ord(initial_letter)
            normalized_test_value = ord(''.join([i for i in unicodedata.normalize("NFKD", initial_letter) if not unicodedata.combining(i)]))
            initial = initial_letter.upper().encode("utf8")
        if test_value in query_range or normalized_test_value in query_range:
            if normalized_test_value in query_range:
                initial = ''.join([i for i in unicodedata.normalize("NFKD", initial_letter) if not unicodedata.combining(i)]).upper().encode('utf8')
            if request.group_by_field == "title":
                url = "navigate/%s/table-of-contents" % doc['philo_id'].split()[0]
            elif not doc[request.metadata_display]:
                metadata_displayed = "NA"
                url = 'query?report=bibliography&%s=NULL' % request.metadata_display
            else:
                metadata_displayed = doc[request.metadata_display]
                url = 'query?report=bibliography&%s="%s"' % (request.metadata_display, metadata_displayed)
            content.append({
                "metadata_display": metadata_displayed,
                "metadata": get_all_metadata(db, doc),
                "url": url,
                "count": doc['count'],
                "initial": initial
            })
    return json.dumps({"display_count": request.display_count, "content_type": content_type, "content": content})


def group_by_metadata(request, db):
    c = db.dbh.cursor()
    query = '''select * from toms where philo_type="doc" and %s=?''' % request.group_by_field
    c.execute(query, (request.query, ))
    content = []
    for doc in c.fetchall():
        content.append({
            "metadata_display": doc["title"] or "NA",
            "metadata": get_all_metadata(db, doc),
            "url": "navigate/%s/table-of-contents" % doc['philo_id'].split()[0],
            "initial": request.query
        })
    return json.dumps({
        "display_count": request.display_count,
        "content_type": request.group_by_field,
        "content": content
    })


def get_all_metadata(db, doc):
    doc_metadata = {}
    for metadata in db.locals.metadata_fields:
        try:
            doc_metadata[metadata] = doc[metadata] or "NA"
        except IndexError:
            doc_metadata[metadata] = "NA"
    return doc_metadata


if __name__ == "__main__":
    CGIHandler().run(landing_page_content)
