#!/usr/bin/env python

from lxml import etree
import sys

"""This script is intended to check if any given XML file
contains a div or div1. If not, it makes the <body> or <text> element
a div.
This script should be called before the parse_files function in the load_script. 
"""

def check_for_divs_in_file(load_metadata, text_dir, xpaths):
    new_load_metadata = []
    modified_files = []
    for pos, f in enumerate(load_metadata):
        file = open(text_dir + f['filename'])
        file_content = file.read()
        root = etree.fromstring(file_content)
        # Remove namespace
        for el in root.iter():
            try:
                if el.tag.startswith('{'):
                    el.tag = el.tag.rsplit('}', 1)[-1]
            except AttributeError: ## el.tag is not a string for some reason
                pass
        div = root.find('.//div')
        if div is not None:
            if "type" in div.attrib and div.attrib["type"] == "notes":  ## Notes don't count
                div = None
        if div is not None:
            continue
        else:
            div1 = root.find('.//div1')
            if div1 is not None:
                continue
            else:
                body = root.find('.//body')
                if body is not None:
                    xpath = [("div", ".//body")]
                    load_metadata[pos]['options'] = {}
                    load_metadata[pos]['options']['xpaths'] = xpaths[0:1] + xpath + xpaths[1:]
                    modified_files.append((f['filename'], xpath))
                else:
                    text = root.find('.//text')
                    if text is not None:
                        xpath = [("div", ".//text")]
                        load_metadata[pos]['options'] = {}
                        load_metadata[pos]['options']['xpaths'] = xpaths[0:1] + xpath + xpaths[1:]
                        modified_files.append((f['filename'], xpath))
    
    if modified_files:
        print("%d files have added a new XPATH to map <body> or <text> to a div:" % len(modified_files), file=sys.stderr)
    for filename, xpath in modified_files: 
        print("%s: %s" % (filename, repr(xpath[0])), file=sys.stderr)
    return load_metadata