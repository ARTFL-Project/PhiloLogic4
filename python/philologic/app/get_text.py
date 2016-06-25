#!/usr/bin/env python

import os
import re

from lxml import etree
from ObjectFormatter import adjust_bytes, format_concordance, format_text_object
from philologic.HitWrapper import ObjectWrapper
from philologic.DB import DB


def get_text(hit, start_byte, length, path):
    file_path = path + '/data/TEXT/' + hit.doc.filename
    text_file = open(file_path)
    text_file.seek(start_byte)
    return text_file.read(length)


def get_concordance_text(db, hit, path, context_size):
    ## Determine length of text needed
    bytes = sorted(hit.bytes)
    byte_distance = bytes[-1] - bytes[0]
    length = context_size + byte_distance + context_size
    bytes, start_byte = adjust_bytes(bytes, context_size)
    conc_text = get_text(hit, start_byte, length, path)
    conc_text = format_concordance(conc_text, db.locals['word_regex'], bytes)
    return conc_text


def get_text_obj(obj, config, request, word_regex, note=False, images=True):
    path = config.db_path
    filename = obj.doc.filename
    if filename and os.path.exists(path + "/data/TEXT/" + filename):
        path += "/data/TEXT/" + filename
    else:
        ## workaround for when no filename is returned with the full philo_id of the object
        philo_id = str(obj.philo_id[0]) + ' 0 0 0 0 0 0'
        c = obj.db.dbh.cursor()
        c.execute("select filename from toms where philo_type='doc' and philo_id =? limit 1", (philo_id, ))
        path += "/data/TEXT/" + c.fetchone()["filename"]
    file = open(path)
    start_byte = int(obj.start_byte)
    file.seek(start_byte)
    width = int(obj.end_byte) - start_byte
    raw_text = file.read(width)
    try:
        bytes = sorted([int(byte) - start_byte for byte in request.byte])
    except ValueError:  ## request.byte contains an empty string
        bytes = []

    formatted_text, imgs = format_text_object(obj, raw_text, config, request, word_regex, bytes=bytes, note=note)
    formatted_text = formatted_text.decode("utf-8", "ignore")
    if images:
        return formatted_text, imgs
    else:
        return formatted_text


def get_tei_header(request, config):
    path = config.db_path
    db = DB(path + "/data")
    obj = ObjectWrapper(request['philo_id'].split(), db)
    filename = path + '/data/TEXT/' + obj.filename
    parser = etree.XMLParser(remove_blank_text=True, recover=True)
    xml_tree = etree.parse(filename, parser)
    header = xml_tree.find("teiHeader")
    try:
        header_text = etree.tostring(header, pretty_print=True)
    except TypeError:  # workaround for when lxml doesn't find the header for whatever reason
        header_text = ''
        start = 0
        for line in open(filename):
            if re.search(r'<teiheader|head', line, re.I):
                start = 1
            if start:
                header_text += line
            if re.search(r'</teiheader|head', line, re.I):
                break
    return header_text.replace('<', '&lt;').replace('>', '&gt;')
