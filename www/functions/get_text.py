#!/usr/bin/env python


def get_text(hit, byte_start, length, path):
    file_path = path + '/data/TEXT/' + hit.doc.filename
    text_file = open(file_path)
    text_file.seek(byte_start)
    return text_file.read(length)
