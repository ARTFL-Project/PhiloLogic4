#!/usr/bin/env python3


import os
import re

from lxml import etree
from philologic.runtime.DB import DB
from philologic.runtime.HitWrapper import ObjectWrapper

from .ObjectFormatter import adjust_bytes, format_concordance, format_text_object


def get_text(hit, start_byte, length, path):
    file_path = path + "/data/TEXT/" + hit.doc.filename
    with open(file_path, "rb") as text_file:
        text_file.seek(start_byte)
        return text_file.read(length)


def get_concordance_text(db, hit, path, context_size):
    ## Determine length of text needed
    byte_offsets = sorted(hit.bytes)
    byte_distance = byte_offsets[-1] - byte_offsets[0]
    length = context_size + byte_distance + context_size
    byte_offsets, start_byte = adjust_bytes(byte_offsets, context_size)
    conc_text = get_text(hit, start_byte, length, path)
    conc_text = format_concordance(conc_text, db.locals["token_regex"], byte_offsets)
    return conc_text


def get_text_obj(obj, config, request, word_regex, note=False, images=True):
    path = config.db_path
    filename = obj.doc.filename
    if filename and os.path.exists(path + "/data/TEXT/" + filename):
        path += "/data/TEXT/" + filename
    else:
        ## workaround for when no filename is returned with the full philo_id of the object
        philo_id = str(obj.philo_id[0]) + " 0 0 0 0 0 0"
        c = obj.db.dbh.cursor()
        c.execute("select filename from toms where philo_type='doc' and philo_id =? limit 1", (philo_id,))
        path += "/data/TEXT/" + c.fetchone()["filename"]
    with open(path, "rb") as file:
        obj_start_byte = int(obj.start_byte)
        file.seek(obj_start_byte)
        width = int(obj.end_byte) - obj_start_byte
        raw_text = file.read(width)
    try:
        byte_offsets = sorted([int(byte) - obj_start_byte for byte in request.byte])
    except ValueError:  ## request.byte contains an empty string
        byte_offsets = []
    if request.start_byte:
        request.start_byte = request.start_byte - obj_start_byte
        request.end_byte = request.end_byte - obj_start_byte
    formatted_text, imgs = format_text_object(
        obj,
        raw_text,
        config,
        request,
        word_regex,
        byte_offsets=byte_offsets,
        note=note,
        images=images,
        start_byte=request.start_byte,
        end_byte=request.end_byte,
    )
    if images:
        return formatted_text, imgs
    else:
        return formatted_text


def get_tei_header(request, config):
    path = config.db_path
    db = DB(path + "/data")
    obj = ObjectWrapper(request["philo_id"].split(), db)
    filename = path + "/data/TEXT/" + obj.filename
    parser = etree.XMLParser(remove_blank_text=True, recover=True)
    xml_tree = etree.parse(filename, parser)
    header = xml_tree.find("teiHeader")
    try:
        header_text = etree.tostring(header, pretty_print=True).decode("utf8")
    except TypeError as e:  # workaround for when lxml doesn't find the header for whatever reason
        start = False
        header_text = ""
        with open(filename, encoding="utf8") as file:
            file_content = file.read()
            try:
                start_header_index = re.search(r"<teiheader", file_content, re.I).start()
                end_header_index = re.search(r"</teiheader>", file_content, re.I).end()
            except AttributeError:  # tag not found
                return ""
            header_text = file_content[start_header_index:end_header_index]
    return header_text.replace("<", "&lt;").replace(">", "&gt;")
