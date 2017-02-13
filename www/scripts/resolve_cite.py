#!/usr/bin/env python3

import os
import re
import sys
from wsgiref.handlers import CGIHandler

from philologic.DB import DB
from philologic.HitWrapper import ObjectWrapper

from philologic.runtime import WSGIHandler


def resolve_cite_service(environ, start_response):
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace('scripts', ''))
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(environ, config)
    c = db.dbh.cursor()
    q = request.q

    best_url = config['db_url']

    if " - " in q:
        milestone = q.split(" - ")[0]
    else:
        milestone = q

    milestone_segments = []
    last_segment = 0
    milestone_prefixes = []
    for separator in re.finditer(r' (?!\.)|\.(?! )', milestone):
        milestone_prefixes += [milestone[:separator.start()]]
        milestone_segments += [milestone[last_segment:separator.start()]]
        last_segment = separator.end()
    milestone_segments += [milestone[last_segment:]]
    milestone_prefixes += [milestone]

    print("SEGMENTS", repr(milestone_segments), file=sys.stderr)
    print("PREFIXES", repr(milestone_prefixes), file=sys.stderr)

    abbrev_match = None
    for pos, v in enumerate(milestone_prefixes):
        print("QUERYING for abbrev = ", v, file=sys.stderr)
        abbrev_q = c.execute("SELECT * FROM toms WHERE abbrev = ?;", (v, )).fetchone()
        if abbrev_q:
            abbrev_match = abbrev_q

    print("ABBREV", abbrev_match["abbrev"], abbrev_match["philo_id"], file=sys.stderr)
    doc_obj = ObjectWrapper(abbrev_match['philo_id'].split(), db)

    nav = nav_query(doc_obj, db)

    best_match = None
    for n in nav:
        if n["head"] == request.q:
            print("MATCH", n["philo_id"], n["n"], n["head"], file=sys.stderr)
            best_match = n
            break

    if best_match:
        type_offsets = {"doc": 1, "div1": 2, "div2": 3, "div3": 4, "para": 5}
        t = best_match['philo_type']
        short_id = best_match["philo_id"].split()[:type_offsets[t]]
        best_url = f.make_absolute_object_link(config, short_id)
        print("BEST_URL", best_url, file=sys.stderr)

    status = '302 Found'
    redirect = config['db_url']
    headers = [('Location', best_url)]
    start_response(status, headers)

    return ""


#TODO: same functionality exists in philologic.reports in the toc code: consolidate
def nav_query(obj, db):
    conn = db.dbh
    c = conn.cursor()
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
    c.execute("select * from toms where rowid >= ? and rowid <=? and philo_type>='div' and philo_type<='div3'",
              (start_rowid, end_rowid))
    for o in c.fetchall():
        philo_id = [int(n) for n in o["philo_id"].split(" ")]
        i = HitWrapper.ObjectWrapper(philo_id, db, row=o)
        yield i


if __name__ == "__main__":
    CGIHandler().run(resolve_cite_service)
