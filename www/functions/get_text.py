#!/usr/bin/env python

import re
import sys

def get_text(hit, byte_start, length, path):
    file_path = path + '/data/TEXT/' + hit.doc.filename
    file = open(file_path)
    file.seek(byte_start)
    return file.read(length)
