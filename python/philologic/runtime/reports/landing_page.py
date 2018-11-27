#!/usr/bin/env python3
"""Landing page reports."""

import json
import sqlite3
import sys
import unicodedata
from collections import defaultdict
from operator import itemgetter

from philologic.DB import DB
from philologic.runtime.citations import citation_links, citations
from philologic.utils import unaccent


def landing_page_bibliography(request, config):
    db = DB(config.db_path + "/data/")
    object_level = request.object_level
    if object_level and object_level in ["doc", "div1", "div2", "div3"]:
        hits = db.get_all(object_level)
    else:
        hits = db.get_all(db.locals["default_object_level"])
    results = []
    c = db.dbh.cursor()
    for hit in hits:
        hit_object = {}
        for field in db.locals["metadata_fields"]:
            hit_object[field] = hit[field] or ""
        if object_level == "doc":
            hit_object["philo_id"] = hit.philo_id[0]
        else:
            hit_object["philo_id"] = "/".join([str(i) for i in hit.philo_id])
        doc_id = str(hit.philo_id[0]) + " 0 0 0 0 0 0"
        next_doc_id = str(hit.philo_id[0] + 1) + " 0 0 0 0 0 0"
        c.execute('select rowid from toms where philo_id="%s"' % doc_id)
        doc_row = c.fetchone()["rowid"]
        c.execute('select rowid from toms where philo_id="%s"' % next_doc_id)
        try:
            next_doc_row = c.fetchone()["rowid"]
        except TypeError:  # if this is the last doc, just get the last rowid in the table.
            c.execute("select max(rowid) from toms;")
            next_doc_row = c.fetchone()[0]
        try:
            c.execute(
                'select * from toms where rowid between %d and %d and head is not null and head !="" limit 1'
                % (doc_row, next_doc_row)
            )
        except sqlite3.OperationalError:  # no type field in DB
            c.execute(
                'select * from toms where rowid between ? and ? and head is not null and head !="" limit 1',
                (doc_row, next_doc_row),
            )
        try:
            start_head = c.fetchone()["head"].decode("utf-8")
            start_head = start_head.lower().title().encode("utf-8")
        except Exception as e:
            print(repr(e), file=sys.stderr)
            start_head = ""
        try:
            c.execute(
                'select head from toms where rowid between %d and %d and head is not null and head !="" order by rowid desc limit 1'
                % (doc_row, next_doc_row)
            )
        except sqlite3.OperationalError:  # no type field in DB
            c.execute(
                'select head from toms where rowid between %d and %d and head is not null and head !="" order by rowid desc limit 1'
                % (doc_row, next_doc_row)
            )
        try:
            end_head = c.fetchone()["head"]
            end_head = end_head.decode("utf-8").lower().title().encode("utf-8")
        except:
            end_head = ""
        hit_object["start_head"] = start_head
        hit_object["end_head"] = end_head

        results.append(hit_object)
    return results


def group_by_range(request_range, request, config):
    db = DB(config.db_path + "/data/")
    metadata_queried = request.group_by_field
    citation_types = json.loads(request.citation)
    is_date = False
    try:
        int(request_range[0])
        int(request_range[1])
        is_date = True
    except ValueError:
        pass

    cursor = db.dbh.cursor()
    if is_date:
        content_type = "date"
        query_range = set(range(int(request_range[0]), int(request_range[1])))
        cursor.execute('select * from toms where philo_type="doc"')
    else:
        content_type = metadata_queried
        query_range = set(range(ord(request_range[0]), ord(request_range[1]) + 1))  # Ordinal avoids unicode issues...
        cursor.execute('select *, count(*) as count from toms where philo_type="doc" group by %s' % metadata_queried)
    try:
        cursor.execute('select *, count(*) as count from toms where philo_type="doc" group by %s' % metadata_queried)
    except sqlite3.OperationalError:
        return json.dumps({"display_count": request.display_count, "content_type": content_type, "content": []})
    content = {}
    date_count = defaultdict(int)
    for doc in cursor:
        normalized_test_value = ""
        if doc[metadata_queried] is None:
            continue
        if is_date:
            try:
                initial = int(doc[metadata_queried])
                test_value = initial
                date_count[initial] += 1
            except:
                continue
        else:
            try:
                initial_letter = doc[metadata_queried][0].lower()
            except IndexError:
                # we have an empty string
                continue
            try:
                test_value = ord(initial_letter)
                normalized_test_value = ord(
                    "".join([i for i in unicodedata.normalize("NFKD", initial_letter) if not unicodedata.combining(i)])
                )
            except TypeError:
                continue
            initial = initial_letter.upper()
        # Are we within the range?
        if test_value in query_range or normalized_test_value in query_range:
            if normalized_test_value in query_range:
                initial = "".join(
                    [i for i in unicodedata.normalize("NFKD", initial_letter) if not unicodedata.combining(i)]
                ).upper()
            obj = db[doc["philo_id"]]
            links = citation_links(db, config, obj)
            citation = citations(obj, links, config, report="landing_page", citation_type=citation_types)
            if initial not in content:
                content[initial] = []
            if is_date:
                try:
                    normalized_field = unaccent.smash_accents(doc["title"]).lower()
                except:
                    normalized_field = None
                content[initial].append(
                    {
                        "metadata": get_all_metadata(db, doc),
                        "citation": citation,
                        "count": date_count[initial],
                        "normalized": normalized_field,
                    }
                )
            else:
                content[initial].append(
                    {
                        "metadata": get_all_metadata(db, doc),
                        "citation": citation,
                        "count": doc["count"],
                        "normalized": unaccent.smash_accents(doc[metadata_queried]).lower(),
                    }
                )
    results = []
    for prefix, result_set in sorted(content.items(), key=itemgetter(0)):
        results.append({"prefix": prefix, "results": sorted(result_set, key=lambda x: x["normalized"])})
    return json.dumps({"display_count": request.display_count, "content_type": content_type, "content": results})


def group_by_metadata(request, config):
    citation_types = json.loads(request.citation)
    db = DB(config.db_path + "/data/")
    cursor = db.dbh.cursor()
    query = """select * from toms where philo_type="doc" and %s=?""" % request.group_by_field
    cursor.execute(query, (request.query,))
    result_group = []
    for doc in cursor:
        obj = db[doc["philo_id"]]
        links = citation_links(db, config, obj)
        citation = citations(obj, links, config, report="landing_page", citation_type=citation_types)
        result_group.append({"metadata": get_all_metadata(db, doc), "citation": citation})
    return json.dumps(
        {
            "display_count": request.display_count,
            "content_type": request.group_by_field,
            "content": [{"prefix": request.query, "results": result_group}],
        }
    )


def get_all_metadata(db, doc):
    doc_metadata = {}
    for metadata in db.locals.metadata_fields:
        try:
            doc_metadata[metadata] = doc[metadata] or "NA"
        except IndexError:
            doc_metadata[metadata] = "NA"
    return doc_metadata
