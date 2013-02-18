#!/usr/bin/env python

def get_text(hit, byte_start, length, path):
    file_path = path + '/data/TEXT/' + hit.filename
    file = open(file_path)        
    file.seek(byte_start)
    return file.read(length)