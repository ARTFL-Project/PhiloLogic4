#!/usr/bin/env python

import sys
import os
import re
from lxml import etree
from philologic.Loader import Loader
from philologic.Parser import DefaultMetadataXPaths


### USAGE ###
# python list_xpaths_in_header.py files

def pre_parse_header(fn):
    fh = open(fn)
    header = ""
    while True:
        line = fh.readline()
        scan = re.search("<teiheader>|<temphead>",line,re.IGNORECASE)
        if scan:
            header = line[scan.start():]
            break
    while True:        
        line = fh.readline()
        scan = re.search("</teiheader>|<\/?temphead>", line, re.IGNORECASE)
        if scan:
            header = header + line[:scan.end()]
            break
        else:
            header = header + line
    tree = etree.fromstring(header)
    for el in tree.iter():
        try:
            if el.tag.startswith('{'):
                el.tag = el.tag.rsplit('}', 1)[-1]
        except AttributeError: ## el.tag is not a string for some reason
            pass
    return tree


def pre_parse_whole_file(fn):
    fh = open(fn)
    tree = etree.fromstring(fh.read())
    # Remove namespace
    for el in tree.iter():
        try:
            if el.tag.startswith('{'):
                el.tag = el.tag.rsplit('}', 1)[-1]
        except AttributeError: ## el.tag is not a string for some reason
            pass
    return tree
    
def retrieve_xpaths(filelist):
    metadata_xpaths = {}
    for fn in filelist:
        print("## XPATHS for %s" % fn)
        tree = pre_parse_header(fn)
        root = tree.getroottree()
        for el in tree.iter():
            if el.getchildren() == [] and el.text != None:
                print(root.getpath(el))
        print()

if __name__ == '__main__':
    xpaths = retrieve_xpaths(sys.argv[1:])