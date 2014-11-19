#!/usr/bin env python

import os
import sys
sys.path.append('..')
import reports as r
import traceback
import py_compile
from json import dumps
from mako.lookup import TemplateLookup
from mako import exceptions
from concatenate_web_resources import webResources

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

template_path = os.path.abspath(os.path.dirname(__file__)).replace('functions', '') + '/templates/'
template_lookup = TemplateLookup(template_path, module_directory='%s/compiled_templates/' % template_path,
                                 collection_size=50, module_writer=compiled_template_permissions)

def render_template(*args, **data):
    config = data['config']
    resource = webResources(data['template_name'], debug=config.debug)
    data['css'] = resource.css
    data['js'] = resource.js
    template = template_lookup.get_template(data['template_name'])
    if not config.debug:
        try:
            return template.render(*args, **data).encode("UTF-8", "ignore")
        except:
            return r.error.error_handling(config, data['q'])
    else:
        try:
            return template.render(*args, **data).encode("UTF-8", "ignore")
        except:
            traceback.print_exc()
            return exceptions.html_error_template().render()
