#!/usr/bin/env python

import sys
import os
import re
from lxml import etree
from philologic.Loader import Loader
from philologic.Parser import DefaultMetadataXPaths


### USAGE ###
# python extract_metadata.py files


def pre_parse_whole_file(fn):
    fh = open(fn)
    tree = etree.fromstring(fh.read())
    # Remove namespace
    for el in tree.iter():
        try:
            if el.tag.startswith("{"):
                el.tag = el.tag.rsplit("}", 1)[-1]
        except AttributeError:  ## el.tag is not a string for some reason
            pass
    return tree


def sort_by_metadata(filelist, metadata_xpaths, *fields, **options):
    load_metadata = []
    if "reverse" in options:
        reverse = options["reverse"]
    else:
        reverse = False

    for fn in filelist:
        data = {"filename": fn}
        tree = pre_parse_whole_file(fn)

        for type, xpath, field in metadata_xpaths:
            if type == "doc":
                if field not in data:
                    attr_pattern_match = re.search(r"@([^\/\[\]]+)$", xpath)
                    if attr_pattern_match:
                        xp_prefix = xpath[: attr_pattern_match.start(0)]
                        attr_name = attr_pattern_match.group(1)
                        elements = tree.findall(xp_prefix)
                        for el in elements:
                            if el is not None and el.get(attr_name, ""):
                                data[field] = el.get(attr_name, "").encode("utf-8")
                                break
                    else:
                        el = tree.find(xpath)
                        if el is not None and el.text is not None:
                            data[field] = el.text.encode("utf-8")
        load_metadata.append(data)

    def make_sort_key(d):
        key = [d.get(f, "") for f in fields]
        return key

    load_metadata.sort(key=make_sort_key, reverse=reverse)
    return load_metadata


if __name__ == "__main__":
    try:
        from artfl_xpaths import metadata_xpaths
    except:
        metadata_xpaths = DefaultMetadataXPaths
    load_metadata = sort_by_metadata(sys.argv[1:], metadata_xpaths)

    for file in load_metadata:
        print("## Metadata found for %s ##" % file["filename"])
        for metadata in file:
            if metadata != "filename":
                print("%s: %s" % (metadata, file[metadata]))
        print()
