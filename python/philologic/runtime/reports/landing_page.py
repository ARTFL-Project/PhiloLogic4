#!/usr/bin/env python3
"""Landing page reports."""

import orjson
import sqlite3
import sys
import unicodedata


from philologic.runtime.DB import DB


def landing_page_bibliography(request, config):
    """Retrieves volumes for dictionary view"""
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
        doc_id = f"{hit.philo_id[0]} 0 0 0 0 0 0"
        next_doc_id = f"{hit.philo_id[0] + 1} 0 0 0 0 0 0"
        c.execute(f'select rowid from toms where philo_id="{doc_id}"')
        doc_row = c.fetchone()["rowid"]
        c.execute(f'select rowid from toms where philo_id="{next_doc_id}"')
        try:
            next_doc_row = c.fetchone()["rowid"]
        except TypeError:  # if this is the last doc, just get the last rowid in the table.
            c.execute("select max(rowid) from toms;")
            next_doc_row = c.fetchone()[0]
        try:
            c.execute(
                f'select * from toms where rowid between {doc_row} and {next_doc_row} and head is not null and head !="" limit 1'
            )
        except sqlite3.OperationalError:  # no type field in DB
            c.execute(
                'select * from toms where rowid between ? and ? and head is not null and head !="" limit 1',
                (doc_row, next_doc_row),
            )
        try:
            start_head = c.fetchone()["head"]
            start_head = start_head.lower().title()
        except Exception as e:
            print(repr(e), file=sys.stderr)
            start_head = ""
        try:
            c.execute(
                f'select head from toms where rowid between {doc_row} and {next_doc_row} and head is not null and head !="" order by rowid desc limit 1'
            )
        except sqlite3.OperationalError:  # no type field in DB
            c.execute(
                f'select head from toms where rowid between {doc_row} and {next_doc_row} and head is not null and head !="" order by rowid desc limit 1'
            )
        try:
            end_head = c.fetchone()["head"]
            end_head = end_head.lower().title()
        except:
            end_head = ""
        hit_object["start_head"] = start_head
        hit_object["end_head"] = end_head

        results.append(hit_object)
    return orjson.dumps(results)


def group_by_range(request_range, request, config):
    """Group metadata by range"""
    db = DB(config.db_path + "/data/")
    metadata_queried = request.group_by_field
    is_date = False
    try:
        int(request_range[0])
        int(request_range[1])
        is_date = True
    except ValueError:
        pass

    metadata_fields_needed, citations = get_fields_and_citations(request, config)
    cursor = db.dbh.cursor()
    content = {}
    if is_date:
        content_type = "date"
        query = f'select * from toms where philo_type="doc" and cast({metadata_queried} as integer) between ? and ?'
        cursor.execute(query, (int(request_range[0]), int(request_range[1])))
        content = {}
        for doc in cursor:
            metadata = {m: doc[m] for m in metadata_fields_needed}
            if metadata[metadata_queried] not in content:
                content[metadata[metadata_queried]] = {"prefix": metadata[metadata_queried], "results": []}
            content[metadata[metadata_queried]]["results"].append(
                {
                    "metadata": metadata,
                    "count": 1,
                }
            )
        return orjson.dumps(
            {
                "display_count": request.display_count,
                "content_type": content_type,
                "content": content,
                "citations": citations,
            }
        )
    content_type = metadata_queried
    query_range = set(range(ord(request_range[0]), ord(request_range[1]) + 1))  # Ordinal avoids unicode issues...
    try:
        cursor.execute(f'select *, count(*) as count from toms where philo_type="doc" group by {metadata_queried}')
    except sqlite3.OperationalError:
        return orjson.dumps({"display_count": request.display_count, "content_type": content_type, "content": []})
    for doc in cursor:
        normalized_test_value = ""
        if doc[metadata_queried] is None:
            continue
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
            metadata = {m: doc[m] for m in metadata_fields_needed}
            if initial not in content:
                content[initial] = {"prefix": initial, "results": []}
            content[initial]["results"].append(
                {
                    "metadata": metadata,
                    "count": doc["count"],
                }
            )
    return orjson.dumps(
        {
            "display_count": request.display_count,
            "content_type": content_type,
            "content": content,
            "citations": citations,
        }
    )


def group_by_metadata(request, config):
    """Count result by metadata field"""
    db = DB(config.db_path + "/data/")
    metadata_fields_needed, citations = get_fields_and_citations(request, config)
    cursor = db.dbh.cursor()
    query = f"""select * from toms where philo_type="doc" and {request.group_by_field}=?"""
    cursor.execute(query, (request.query,))
    result_group = []
    for doc in cursor:
        metadata = {}
        for m in metadata_fields_needed:
            try:
                metadata[m] = doc[m]
            except IndexError:
                pass
        result_group.append(
            {
                "metadata": metadata,
            }
        )
    return orjson.dumps(
        {
            "display_count": request.display_count,
            "content_type": request.group_by_field,
            "content": [{"prefix": request.query, "results": result_group}],
            "citations": citations,
        }
    )


def get_fields_and_citations(request, config):
    """Get fields and citations"""
    metadata_fields_needed = [request.group_by_field, "philo_id"]
    citations = []
    for conf in config.default_landing_page_browsing:
        if conf["group_by_field"] == request.group_by_field:
            for citation in conf["citation"]:
                citations.append(citation)
                metadata_fields_needed.append(citation["field"])
            break
    return metadata_fields_needed, citations
