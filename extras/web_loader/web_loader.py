#!/usr/bin/env python

import os
import sys
from cgi import FieldStorage
from glob import glob
from simplejson import dumps
from wsgiref.handlers import CGIHandler

from philologic.Loader import Loader, setup_db_dir
from philologic.LoadOptions import LoadOptions

os.environ["LC_ALL"] = "C"  # Exceedingly important to get uniform sort order.
os.environ["PYTHONIOENCODING"] = "utf-8"


def web_loader(environ, start_response):
    headers = [('Content-type', 'application/json; charset=UTF-8'), ("Access-Control-Allow-Origin", "*")]
    start_response('200 OK', headers)

    form = FieldStorage()
    pid = os.fork()
    if pid == 0:  # new process
        os.system("philoload4 %s %s &" % (form.getvalue("dbname"), form.getvalue("files")))
        exit()

    yield dumps({"success": True})


if __name__ == "__main__":
    CGIHandler().run(web_loader)
