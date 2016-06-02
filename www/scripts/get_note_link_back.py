#!/usr/bin/env python

import os
import subprocess
from bisect import bisect_left
from wsgiref.handlers import CGIHandler

import simplejson
from philologic.DB import DB
from philologic.HitWrapper import ObjectWrapper

from philologic.app import WebConfig
from philologic.app import WSGIHandler


def get_note_link_back(environ, start_response):
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace('scripts', ''))
    request = WSGIHandler(environ, config)

    # Get byte offset of hash
    db = DB(config.db_path + '/data/')
    path = config.db_path
    philo_id = request.doc_id + ' 0 0 0 0 0 0'
    obj = ObjectWrapper(philo_id.split(), db)
    filename = path + '/data/TEXT/' + obj.filename

    match = request.note_id + '\|' + request.note_id.replace('#', '')
    proc = subprocess.Popen(
        ['grep', '-o', '--byte-offset', match, filename],
        stdout=subprocess.PIPE)
    output = proc.communicate()[0]
    first_hit = output.split('\n')[0]
    note_offset = int(first_hit.split(':')[0].strip())

    # Get all div1s in document
    c = db.dbh.cursor()
    doc_id = int(request.doc_id)
    next_doc_id = doc_id + 1
    # find the starting rowid for this doc
    c.execute('select rowid from toms where philo_id="%d 0 0 0 0 0 0"' %
              doc_id)
    start_rowid = c.fetchone()[0]
    # find the starting rowid for the next doc
    c.execute('select rowid from toms where philo_id="%d 0 0 0 0 0 0"' %
              next_doc_id)
    try:
        end_rowid = c.fetchone()[0]
    except TypeError:  # if this is the last doc, just get the last rowid in the table.
        c.execute('select max(rowid) from toms;')
        end_rowid = c.fetchone()[0]

    c.execute(
        'select byte_start, philo_id from toms where rowid >= ? and rowid <=? and philo_type="div1"',
        (start_rowid, end_rowid))
    results = [(i['byte_start'], i['philo_id']) for i in c.fetchall()]
    closest_byte = takeClosest([i[0] for i in results], note_offset)
    result_id = dict(results)[closest_byte]
    link = 'navigate/' + \
        '/'.join(result_id.split()[:2]) + \
        '#%s-link-back' % request.note_id.replace('#', '')
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),
               ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    yield simplejson.dumps({'link': link, "h": result_id})


def takeClosest(array, number):
    pos = bisect_left(array, number)
    if pos == 0:
        return array[0]
    elif pos == len(array):
        return array[-1]
    else:
        return array[pos - 1]


if __name__ == "__main__":
    CGIHandler().run(get_note_link_back)
