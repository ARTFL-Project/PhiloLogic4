#!/usr/bin/env python

import re
import sys

def get_text(hit, byte_start, length, path):
    ## We know we want docs, so minimize the number iterations in HitWrapper to get the filename
    file_path = path + '/data/TEXT/' + hit.doc.filename
    file = open(file_path)
    file.seek(byte_start)
    return file.read(length)
