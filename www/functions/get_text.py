#!/usr/bin/env python

import re
import sys
from os.path import exists
from ObjectFormatter import format, format_concordance

def get_text(hit, byte_start, length, path):
    file_path = path + '/data/TEXT/' + hit.filename
    file = open(file_path)        
    file.seek(byte_start)
    return file.read(length)

def get_page_text(db, obj, page_num, path, bytes):
    page = obj.get_page()
    print >> sys.stderr, "OBJ_ID", obj.philo_id,
    print >> sys.stderr, "TYPE", obj.type
    print >> sys.stderr, 'PAGE', obj.page
    print >> sys.stderr, 'PHILO_ID', page['philo_id']
    length = int(page['end_byte']) - int(page['start_byte'])
    file_path = path + '/data/TEXT/' + obj.filename
    file = open(file_path)        
    file.seek(page['start_byte'])
    text = file.read(length)
    sorted_bytes = sorted(bytes.split('+'))
    if bytes and int(page['start_byte']) < int(sorted_bytes[0]) < int(page['end_byte']):
        bytes = sorted([int(byte) - int(page['start_byte']) for byte in bytes.split('+')])
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

    page_obj = obj.get_page()
    if page_obj:
            if page_obj['n'] and page_obj['img']:
                find_head = re.search("<head>([^>]*?)</head>",raw_text)
                if find_head:
                    start_head = find_head.start(0)
                    end_head = find_head.end(0)
                    raw_text = raw_text[:start_head] + "<head>"+find_head.group(1)+" <pb class=\"inserted-page\" n=\"%s\" fac=\"%s\"/>" % (page_obj['n'], page_obj['img']) + "</head>"+ raw_text[end_head:]
    if query_args:
        bytes = sorted([int(byte) - byte_start for byte in query_args.split('+')])
    else:
        bytes = []
    return format(raw_text,bytes).decode("utf-8","ignore")
