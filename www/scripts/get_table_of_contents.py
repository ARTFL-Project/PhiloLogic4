#!/usr/bin/env python

import os
import sys
sys.path.append('..')
from functions.wsgi_handler import parse_cgi
from philologic.HitWrapper import ObjectWrapper
from mako.template import Template
import reports as r
import functions as f

obj_level = {'doc': 1, 'div1': 2, 'div2': 3, 'div3': 4}

if __name__ == "__main__":
    environ = os.environ
    environ["SCRIPT_FILENAME"] = environ["SCRIPT_FILENAME"].replace('scripts/get_table_of_contents.py', '')
    path = environ["SCRIPT_FILENAME"]
    db, path_components, q = parse_cgi(environ)
    obj = ObjectWrapper(q['philo_id'].split(), db)
    mytemplate = Template(filename=path + "templates/toc.mako")
    print "Content-Type: text/html\n"
    print mytemplate.render(obj=obj,db=db,f=f,navigate_doc=r.navigate_doc).encode('utf-8', 'ignore')