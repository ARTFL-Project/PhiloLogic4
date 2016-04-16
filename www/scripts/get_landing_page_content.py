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


def landing_page_content(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'), ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    if type(request.range) == str:
        request_range = request.range.decode("utf8")
    request_range = request_range.lower().split('-')
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
    if request.group_by_field == "title":
        prefixes = '|'.join([i for i in config.title_prefix_removal])
        prefix_sub = re.compile(r"^%s" % prefixes, re.I | re.U)
    for i in c.fetchall():
        if i[request.group_by_field] is None:
            continue
        if is_date:
            try:
                initial = int(i[request.group_by_field])
                test_value = initial
            except:
                continue
        elif request.group_by_field == "title":
            title = i['title'].decode('utf-8').lower()
            title = prefix_sub.sub('', title).strip()
            initial = title[0].upper().encode('utf8')
            test_value = ord(title[0].lower())
        else:
            initial = i[request.group_by_field].decode('utf-8')[0].upper().encode("utf8")
            test_value = ord(i[request.group_by_field].decode('utf8')[0].lower())
        if test_value not in query_range:
            continue
        if not i[request.metadata_display]:
            metadata_displayed = "NA"
            url = 'query?report=bibliography&%s=NULL' % request.metadata_display
        else:
            metadata_displayed = i[request.metadata_display]
            url = 'query?report=bibliography&%s="%s"' % (request.metadata_display, metadata_displayed)

        content.append({
            "metadata_display": metadata_displayed,
            "author": i["author"] or "NA",
            "title": i["title"] or "NA",
            "url": url,
            "count": i['count'],
            "initial": initial
        })
    yield json.dumps({
        "display_count": request.display_count,
        "content_type": content_type,
        "content": content
    })

def date_range(query_range):
    is_date = False
    try:
        int(query_range[0])
        int(query_range[1])
        is_date = True
    except ValueError:
        pass
    return is_date


if __name__ == "__main__":
    CGIHandler().run(landing_page_content)
