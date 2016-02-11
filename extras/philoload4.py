#!/usr/bin/env python

import os
import sys

from philologic.LoadOptions import LoadOptions
from philologic.Loader import Loader

os.environ["LC_ALL"] = "C"  # Exceedingly important to get uniform sort order.
os.environ["PYTHONIOENCODING"] = "utf-8"


if __name__ == '__main__':
    load_options = LoadOptions()
    load_options.parse(sys.argv)

    # Database load
    l = Loader(**load_options.values)
    l.add_files(load_options.files)
    load_metadata = l.sort_by_metadata(*load_options.sort_order, whole_file=True)
    l.parse_files(load_options.cores, load_metadata)
    l.merge_objects()
    l.analyze()
    l.setup_sql_load()
    l.post_processing()
    l.finish()

    print "Application viewable at %s\n" % load_options.db_url
