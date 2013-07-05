#!/usr/bin env python

import os
from json import dumps
from mako.template import Template
from mako.lookup import TemplateLookup
from mako import exceptions

def render_template(*args, **data):
    db = data["db"]
    data['db_locals'] = dumps(db.locals)
    path = os.getcwd().replace('reports', '')
    templates = TemplateLookup(path)
    template = Template(filename="templates/%s" % data['template_name'], lookup=templates)
    try:
        return template.render(*args, **data).encode("UTF-8", "ignore")
    except:
        if not db.locals['debug']:
            template = Template(filename="templates/error.mako", lookup=templates)
            return template.render(*args, **data).encode("UTF-8", "ignore")
        else:
            return exceptions.html_error_template().render()