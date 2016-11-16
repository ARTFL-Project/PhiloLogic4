#!/usr/bin/env python
"""Landing page reports."""

import sqlite3
import sys
import unicodedata
from operator import itemgetter

import simplejson
from philologic.app.citations import citation_links, citations
from philologic.DB import DB


def landing_page_bibliography(request, config):
    db = DB(config.db_path + '/data/')
    object_level = request.object_level
    if object_level and object_level in ["doc", "div1", "div2", "div3"]:
        hits = db.get_all(object_level)
    else:
        hits = db.get_all(db.locals['default_object_level'])
    results = []
    c = db.dbh.cursor()
    for hit in hits:
        hit_object = {}
        for field in db.locals['metadata_fields']:
            hit_object[field] = hit[field] or ''
        if object_level == "doc":
            hit_object['philo_id'] = hit.philo_id[0]
        else:
            hit_object['philo_id'] = '/'.join([str(i) for i in hit.philo_id])
        doc_id = str(hit.philo_id[0]) + ' 0 0 0 0 0 0'
        next_doc_id = str(hit.philo_id[0] + 1) + ' 0 0 0 0 0 0'
        c.execute('select rowid from toms where philo_id="%s"' % doc_id)
        doc_row = c.fetchone()['rowid']
        c.execute('select rowid from toms where philo_id="%s"' % next_doc_id)
        try:
            next_doc_row = c.fetchone()['rowid']
        except TypeError:  # if this is the last doc, just get the last rowid in the table.
            c.execute('select max(rowid) from toms;')
            next_doc_row = c.fetchone()[0]
        try:
            c.execute(
                'select * from toms where rowid between %d and %d and head is not null and head !="" and type !="editorial" and type !="misc" and type !="Misc" and type != "Avertissement" and type != "Title Page" and type != "Avis" limit 1'
                % (doc_row, next_doc_row))
        except sqlite3.OperationalError:  # no type field in DB
            c.execute(
                'select * from toms where rowid between %d and %d and head is not null and head !="" limit 1'
                % (doc_row, next_doc_row))
        try:
            start_head = c.fetchone()['head'].decode('utf-8')
            start_head = start_head.lower().title().encode('utf-8')
        except Exception as e:
            print >> sys.stderr, repr(e)
            start_head = ''
        try:
            c.execute(
                'select head from toms where rowid between %d and %d and head is not null and head !="" and type !="notes" and type !="editorial" and type !="misc" and type !="Misc" and type != "Avertissement" and type != "Title Page" and type != "Avis" order by rowid desc limit 1'
                % (doc_row, next_doc_row))
        except sqlite3.OperationalError:  # no type field in DB
            c.execute(
                'select head from toms where rowid between %d and %d and head is not null and head !="" order by rowid desc limit 1'
                % (doc_row, next_doc_row))
        try:
            end_head = c.fetchone()['head']
            end_head = end_head.decode('utf-8').lower().title().encode('utf-8')
        except:
            end_head = ''
        hit_object['start_head'] = start_head
        hit_object['end_head'] = end_head

        results.append(hit_object)
    return results


def group_by_range(request_range, request, config):
    db = DB(config.db_path + '/data/')
    metadata_queried = request.group_by_field
    citation_types = simplejson.loads(request.citation)
    is_date = False
    try:
        int(request_range[0])
        int(request_range[1])
        is_date = True
    except ValueError:
        pass
    if is_date:
        content_type = "date"
        query_range = set(range(int(request_range[0]), int(request_range[1])))
    else:
        content_type = metadata_queried
        query_range = set(range(
            ord(request_range[0]),
            ord(request_range[1]) + 1))  # Ordinal avoids unicode issues...
    c = db.dbh.cursor()
    c.execute(
        'select *, count(*) as count from toms where philo_type="doc" group by %s'
        % metadata_queried)
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
            normalized_test_value = ord(''.join(
                [i
                 for i in unicodedata.normalize("NFKD", initial_letter)
                 if not unicodedata.combining(i)]))
            initial = initial_letter.upper().encode("utf8")
        # Are we within the range?
        if test_value in query_range or normalized_test_value in query_range:
            if normalized_test_value in query_range:
                initial = ''.join(
                    [i
                     for i in unicodedata.normalize("NFKD", initial_letter)
                     if not unicodedata.combining(i)]).upper().encode('utf8')
            obj = db[doc["philo_id"]]
            links = citation_links(db, config, obj)
            citation = citations(obj, links, config, report="landing_page", citation_type=citation_types)
            if initial not in content:
                content[initial] = []
            content[initial].append({
                "metadata": get_all_metadata(db, doc),
                "citation": citation,
                "count": doc['count']
            })
    results = []
    for result_set in sorted(content.iteritems(), key=itemgetter(0)):
        results.append({"prefix": result_set[0], "results": result_set[1]})
    return simplejson.dumps({"display_count": request.display_count,
                             "content_type": content_type,
                             "content": results})


def group_by_metadata(request, config):
    citation_types = simplejson.loads(request.citation)
    db = DB(config.db_path + '/data/')
    c = db.dbh.cursor()
    query = '''select * from toms where philo_type="doc" and %s=?''' % request.group_by_field
    c.execute(query, (request.query, ))
    result_group = []
    for doc in c.fetchall():
        obj = db[doc["philo_id"]]
        links = citation_links(db, config, obj)
        citation = citations(obj, links, config, report="landing_page", citation_type=citation_types)
        result_group.append({
            "metadata": get_all_metadata(db, doc),
            "citation": citation
        })
    return simplejson.dumps({
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
