#!/usr/bin env python

import os
import sys
from json import dumps
from mako.lookup import TemplateLookup
from mako import exceptions
import py_compile
from error import error_handling

def compiled_template_permissions(source, output_path):
    fh = open(output_path, 'w')
    fh.write(source)
    fh.close()
    py_compile.compile(output_path)
    try:
        os.chmod(output_path, 0777)
    except OSError:
        pass
    os.chmod(output_path + 'c', 0777)

template_path = os.getcwd() + '/templates/'
template_lookup = TemplateLookup(template_path, module_directory='%s/compiled_templates/' % template_path,
                                 collection_size=50, module_writer=compiled_template_permissions)

def render_template(*args, **data):
    db = data["db"]
    data['db_locals'] = dumps(db.locals)
    template = template_lookup.get_template(data['template_name'])
    if not db.locals['debug']:
        try:
            return template.render(*args, **data).encode("UTF-8", "ignore")
        except:
            return error_handling(data['db'], data['dbname'], data['q'])
    else:
        try:
            return template.render(*args, **data).encode("UTF-8", "ignore")
        except:
            return exceptions.html_error_template().render()
