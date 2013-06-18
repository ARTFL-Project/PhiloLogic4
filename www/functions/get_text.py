#!/usr/bin/env python

import re
from os.path import exists
from ObjectFormatter import format, format_concordance

def get_text(hit, byte_start, length, path):
    file_path = path + '/data/TEXT/' + hit.filename
    file = open(file_path)        
    file.seek(byte_start)
    return file.read(length)

def get_page_text(db, philo_id, page_num, filename, path, bytes):
    philo_id = str(philo_id) + ' %'
    conn = db.dbh
    c = conn.cursor()
    c.execute("select start_byte, end_byte from pages where philo_id like ? and n=? limit 1", (philo_id,page_num))
    try:
        start_byte, end_byte = c.fetchone()
    except TypeError:   ## returns None because there are no pages in the doc
        return ''
    length = int(end_byte) - int(start_byte)
    file_path = path + '/data/TEXT/' + filename
    file = open(file_path)        
    file.seek(start_byte)
    text = file.read(length)
    sorted_bytes = sorted(bytes.split('+'))
    if bytes and int(start_byte) < int(sorted_bytes[0]) < int(end_byte):
        bytes = sorted([int(byte) - int(start_byte) for byte in bytes.split('+')])
        return format(text, bytes).decode('utf-8', 'ignore')
    else:
        return format(text).decode("utf-8","ignore")
    
def get_text_obj(obj, path, query_args=False):
    filename = obj.filename
    if filename and exists(path + "/data/TEXT/" + filename):
        path += "/data/TEXT/" + filename
    else:
        ## workaround for when no filename is returned with the full philo_id of the object
        philo_id = obj.philo_id[0] + ' 0 0 0 0 0 0'
        c = obj.db.dbh.cursor()
        c.execute("select filename from toms where philo_type='doc' and philo_id =? limit 1", (philo_id,))
        path += "data/TEXT/" + c.fetchone()["filename"]
    file = open(path)
    byte_start = obj.byte_start
    file.seek(byte_start)
    width = obj.byte_end - byte_start
    raw_text = file.read(width)
    if query_args:
        bytes = sorted([int(byte) - byte_start for byte in query_args.split('+')])
    else:
        bytes = []
    return format(raw_text,bytes).decode("utf-8","ignore")