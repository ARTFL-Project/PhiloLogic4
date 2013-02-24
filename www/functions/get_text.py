#!/usr/bin/env python

import re
from format import chunkifier, formatter

def get_text(hit, byte_start, length, path):
    file_path = path + '/data/TEXT/' + hit.filename
    file = open(file_path)        
    file.seek(byte_start)
    return file.read(length)

def get_page_text(db, philo_id, page_num, filename, path, bytes):
    philo_id = philo_id + ' %'
    conn = db.dbh
    c = conn.cursor()
    c.execute("select start_byte, end_byte from pages where philo_id like ? and n=? limit 1", (philo_id,page_num))
    start_byte, end_byte = c.fetchone()
    length = int(end_byte) - int(start_byte)
    file_path = path + '/data/TEXT/' + filename
    file = open(file_path)        
    file.seek(start_byte)
    text = file.read(length)
    if bytes and start_byte < sorted(bytes.split('+'))[0]:
        bytes = sorted([int(byte) - start_byte for byte in bytes.split('+')])
        text_start, text_middle, text_end = chunkifier(text, bytes, highlight=True)
        text = text_start + text_middle + text_end
        text = re.sub('<(/?span[^>]*)>', '[\\1]', text)
        text = formatter(text).decode("utf-8","ignore")
        text = text.replace('[', '<').replace(']', '>')
        return text
    else:
        return formatter(text).decode("utf-8","ignore")   