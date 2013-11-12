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
    results = r.navigate_doc(obj, db)
    html = '<div id="table_of_contents" class="table_of_contents" style="display:block;">'
    for i in results:
        id = i.philo_id[:7]
        link_id = '_'.join([str(j) for j in i.philo_id])
        href = f.link.make_absolute_object_link(db,id)
        head_or_type = i.head or "[%s]" % i.type
        if i.type == "div2":
            spacing = "&nbsp;-&nbsp;"
        elif i.type == "div3":
            spacing = "&nbsp;&nbsp;&nbsp;-&nbsp;"       
        else:
            spacing = ""
        html += spacing
        html += '<a href="%s" id="%s">%s</a><br>' % (href, link_id, head_or_type)
    html += "</div>"
    print "Content-Type: text/html\n"
    print html.encode('utf-8', 'ignore')