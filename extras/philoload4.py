#!/usr/bin/env python

import os
import sys

from philologic.LoadOptions import LoadOptions
from philologic.Loader import Loader, setup_db_dir

os.environ["LC_ALL"] = "C"  # Exceedingly important to get uniform sort order.
os.environ["PYTHONIOENCODING"] = "utf-8"

if __name__ == '__main__':
    load_options = LoadOptions()
    load_options.parse(sys.argv)
    setup_db_dir(load_options["db_destination"], load_options["web_app_dir"], force_delete=load_options.force_delete)

    # Database load
    l = Loader(**load_options.values)
    l.add_files(load_options.files)
    if load_options.bibliography:
        load_metadata = l.parse_bibliography_file(load_options.bibliography, load_options.sort_order)
        print load_metadata
    else:
        load_metadata = l.parse_metadata(load_options.sort_order, header=load_options.header)
    l.parse_files(load_options.cores, load_metadata)
    l.merge_objects()
    l.analyze()
    l.setup_sql_load()
    l.post_processing()
    l.finish()

    print "Application viewable at %s\n" % load_options.db_url
