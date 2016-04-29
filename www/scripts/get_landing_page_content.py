#!/usr/bin/env python

import re
import sys
import unicodedata
from operator import itemgetter
from wsgiref.handlers import CGIHandler

from philologic.DB import DB

sys.path.append('..')
import functions as f
from functions.wsgi_handler import WSGIHandler

try:
    import simplejson as json
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
    metadata_queried = request.group_by_field
    is_date = date_range(request_range)
    if is_date:
        content_type = "date"
        query_range = set(range(int(request_range[0]), int(request_range[1])))
    else:
        content_type = metadata_queried
        query_range = set(range(ord(request_range[0]), ord(request_range[1]) + 1))  # Ordinal avoids unicode issues...
    c = db.dbh.cursor()
    c.execute('select *, count(*) as count from toms where philo_type="doc" group by %s' % metadata_queried)
    content = {}
    for doc in c.fetchall():
        normalized_test_value = ''
        if doc[metadata_queried] is None:
            continue
        if is_date:
            try:
                initial = int(doc[metadata_queried])
                test_value = initial
            except:
                continue
        else:
            initial_letter = doc[metadata_queried].decode('utf-8')[0].lower()
            test_value = ord(initial_letter)
            normalized_test_value = ord(''.join([i for i in unicodedata.normalize("NFKD", initial_letter) if not unicodedata.combining(i)]))
            initial = initial_letter.upper().encode("utf8")
        # Are we within the range?
        if test_value in query_range or normalized_test_value in query_range:
            if normalized_test_value in query_range:
                initial = ''.join([i for i in unicodedata.normalize("NFKD", initial_letter) if not unicodedata.combining(i)]).upper().encode('utf8')
            if metadata_queried == "title":
                url = "navigate/%s/table-of-contents" % doc['philo_id'].split()[0]
            elif not doc[metadata_queried]:
                url = 'query?report=bibliography&%s=NULL' % metadata_queried
            else:
                url = 'query?report=bibliography&%s="%s"' % (metadata_queried, doc[metadata_queried])
            if initial not in content:
                content[initial] = []
            content[initial].append({
                "metadata": get_all_metadata(db, doc),
                "url": url,
                "count": doc['count']
            })
    results = []
    for result_set in sorted(content.iteritems(), key=itemgetter(0)):
        results.append({"prefix": result_set[0], "results": result_set[1]})
    return json.dumps({"display_count": request.display_count, "content_type": content_type, "content": results})


def group_by_metadata(request, db):
    c = db.dbh.cursor()
    query = '''select * from toms where philo_type="doc" and %s=?''' % request.group_by_field
    c.execute(query, (request.query, ))
    result_group = []
    for doc in c.fetchall():
        result_group.append({
            "metadata": get_all_metadata(db, doc),
            "url": "navigate/%s/table-of-contents" % doc['philo_id'].split()[0]
        })
    return json.dumps({
        "display_count": request.display_count,
        "content_type": request.group_by_field,
        "content": [{
            "prefix": request.query,
            "results": result_group
        }]
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
