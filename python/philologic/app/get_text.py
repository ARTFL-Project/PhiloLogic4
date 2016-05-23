#!/usr/bin/env python

import os
import re

from lxml import etree
from ObjectFormatter import adjust_bytes, format_concordance, format_text_object
from philologic.HitWrapper import ObjectWrapper


def get_text(hit, byte_start, length, path):
    file_path = path + '/data/TEXT/' + hit.doc.filename
    text_file = open(file_path)
    text_file.seek(byte_start)
    return text_file.read(length)


def get_concordance_text(db, hit, path, context_size):
    ## Determine length of text needed
    bytes = sorted(hit.bytes)
    byte_distance = bytes[-1] - bytes[0]
    length = context_size + byte_distance + context_size
    bytes, byte_start = adjust_bytes(bytes, context_size)
    conc_text = get_text(hit, byte_start, length, path)
    conc_text = format_concordance(conc_text, db.locals['word_regex'], bytes)
    return conc_text


def get_text_obj(obj, config, request, word_regex, note=False):
    path = config.db_path
    filename = obj.doc.filename
    if filename and os.path.exists(path + "/data/TEXT/" + filename):
        path += "/data/TEXT/" + filename
    else:
        ## workaround for when no filename is returned with the full philo_id of the object
        philo_id = obj.philo_id[0] + ' 0 0 0 0 0 0'
        c = obj.db.dbh.cursor()
        c.execute(
            "select filename from toms where philo_type='doc' and philo_id =? limit 1",
            (philo_id, ))
        path += "/data/TEXT/" + c.fetchone()["filename"]
    file = open(path)
    byte_start = int(obj.byte_start)
    file.seek(byte_start)
    width = int(obj.byte_end) - byte_start
    raw_text = file.read(width)
    try:
        bytes = sorted([int(byte) - byte_start for byte in request.byte])
    except ValueError:  ## request.byte contains an empty string
        bytes = []

    formatted_text, imgs = format_text_object(obj,
                                              raw_text,
                                              config,
                                              request,
                                              word_regex,
                                              bytes=bytes,
                                              note=note)
    formatted_text = formatted_text.decode("utf-8", "ignore")
    return formatted_text, imgs


def get_tei_header(request, config):
    path = config.db_path
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
            if re.search('<%s' % header_name, line):
                start = 1
            if start:
                header_text += line
            if re.search('</%s' % header_name, line):
                break
    return header_text.replace('<', '&lt;').replace('>', '&gt;')
