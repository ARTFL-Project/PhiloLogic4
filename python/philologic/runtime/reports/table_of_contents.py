#!/usr/bin/env python
"""Table of contents"""

from philologic.DB import DB
from philologic.runtime.link import make_absolute_object_link
from philologic import HitWrapper
from philologic.runtime.citations import citations, citation_links


def generate_toc_object(request, config):
    """This function fetches all philo_ids for div elements within a doc"""
    db = DB(config.db_path + '/data/')
    conn = db.dbh
    c = conn.cursor()
    try:
        obj = db[request.philo_id]
    except ValueError:
        philo_id = ' '.join(request.path_components[:-1])
        obj = db[philo_id]
    doc_id = int(obj.philo_id[0])
    next_doc_id = doc_id + 1
    # find the starting rowid for this doc
    c.execute('select rowid from toms where philo_id="%d 0 0 0 0 0 0"' % doc_id)
    start_rowid = c.fetchone()[0]
    # find the starting rowid for the next doc
    c.execute('select rowid from toms where philo_id="%d 0 0 0 0 0 0"' % next_doc_id)
    try:
        end_rowid = c.fetchone()[0]
    except TypeError:  # if this is the last doc, just get the last rowid in the table.
        c.execute('select max(rowid) from toms;')
        end_rowid = c.fetchone()[0]

    # use start_rowid and end_rowid to fetch every div in the document.
    philo_slices = {"doc": 1, "div1": 2, "div2": 3, "div3": 4, "para": 5}
    text_hierarchy = []
    c.execute("select * from toms where rowid >= ? and rowid <=? and philo_type>='div' and philo_type<='div3'",
              (start_rowid, end_rowid))
    for row in c.fetchall():
        philo_id = [int(n) for n in row["philo_id"].split(" ")]
        text = HitWrapper.ObjectWrapper(philo_id, db, row=row)
        if text['philo_name'] == '__philo_virtual' and text["philo_type"] != "div1":
            continue
        elif text['word_count'] == 0:
            continue
        else:
            philo_id = text['philo_id']
            philo_type = text['philo_type']
            display_name = ""
            if text['philo_name'] == "front":
                display_name = "Front Matter"
            elif text['philo_name'] == "note":
                continue
            else:
                display_name = text['head']
                if display_name:
                    display_name = display_name.strip()
                if not display_name:
                    if text["type"] and text["n"]:
                        display_name = text['type'] + " " + text["n"]
                    else:
                        display_name = text["head"] or text['type'] or text['philo_name'] or text['philo_type']
                        if display_name == "__philo_virtual":
                            display_name = text['philo_type']
            display_name = display_name[0].upper() + display_name[1:]
            link = make_absolute_object_link(config, philo_id.split()[:philo_slices[philo_type]])
            philo_id = ' '.join(philo_id.split()[:philo_slices[philo_type]])
            toc_element = {"philo_id": philo_id, "philo_type": philo_type, "label": display_name, "href": link}
            text_hierarchy.append(toc_element)
    metadata_fields = {}
    for metadata in db.locals['metadata_fields']:
        if db.locals['metadata_types'][metadata] == "doc":
            metadata_fields[metadata] = obj[metadata]
    citation_hrefs = citation_links(db, config, obj)
    citation = citations(obj, citation_hrefs, config, report="table_of_contents")
    toc_object = {"query": dict([i for i in request]),
                  "philo_id": obj.philo_id,
                  "toc": text_hierarchy,
                  "metadata_fields": metadata_fields,
                  "citation": citation}
    return toc_object
