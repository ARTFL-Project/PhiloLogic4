#!/usr/bin/env python

import os.path
from web_config import WebConfig

config = WebConfig()
theme = config.theme

default_css = ["split/style.css", "split/searchForm.css", "split/%s" % theme]
css_files = {"landing_page.mako": default_css + ["split/landingPage.css", "split/%s" % theme],
            "concordance.mako": default_css + ["split/concordanceKwic.css", "split/%s" % theme],
            "kwic.mako": default_css + ["split/concordanceKwic.css", "split/%s" % theme],
            "concordance_from_collocation.mako": default_css + ["split/concordanceKwic.css", "split/%s" % theme],
            "word_property_filter.mako": default_css + ["split/concordanceKwic.css", "split/%s" % theme],
            "bibliography.mako": default_css + ["split/concordanceKwic.css", "split/%s" % theme],
            "collocation.mako": default_css + ["split/%s" % theme],
            "time_series.mako": default_css + ["split/timeSeries.css", "split/%s" % theme],
            "text_object.mako": ["image_gallery/blueimp-gallery.min.css"] + default_css +  ["split/textObjectNavigation.css", "split/%s" % theme],
            "t_o_c.mako": default_css + ["split/textObjectNavigation.css", "split/%s" % theme]}

default_js = ['bootstrap/bootstrap.min.js', "plugins/jquery.history.js", "plugins/velocity.min.js", "plugins/velocity.ui.min.js", "plugins/jquery-ui.min.js"]
js_files = {"landing_page.mako": default_js + ["split/common.js", "split/landingPage.js"],
            "concordance.mako": default_js + ["split/common.js", "plugins/jquery.slimscroll.min.js", "split/sidebar.js", "plugins/jquery.hoverIntent.minified.js", "split/concordanceKwic.js"],
            "kwic.mako": default_js + ["split/common.js", "plugins/jquery.slimscroll.min.js", "split/sidebar.js", "plugins/jquery.hoverIntent.minified.js", "split/concordanceKwic.js"],
            "time_series.mako": default_js +["split/common.js", "split/timeSeries.js"],
            "collocation.mako": default_js + ["split/common.js", "plugins/jquery.tagcloud.js", "split/collocation.js"],
            "ranked_relevance.mako": default_js + ["split/common.js", "split/rankedRelevance.js"],
            "bibliography.mako": default_js + ["split/common.js", "plugins/jquery.slimscroll.min.js", "split/sidebar.js", "split/bibliography.js"],
            "text_object.mako": default_js + ["plugins/jquery.blueimp-gallery.min.js", "split/common.js", "plugins/jquery.scrollTo.min.js", "split/textObjectNavigation.js"],
            "concordance_from_collocation.mako": default_js + ["split/common.js", "split/concordanceFromCollocation.js"],
            "word_property_filter.mako": default_js + ["split/common.js", "split/concordanceFromCollocation.js"],
            "t_o_c.mako": default_js + ["split/common.js", "split/toc.js"],
            "error.mako": default_js,
            "access_denied.mako": default_js}


class cssFiles(object):
    
    def __init__(self):
        self.css = css_files
        
    def __getitem__(self, item):
        try:
            return self.css[item]
        except KeyError:
            return default_css


class jsFiles(object):
    
    def __init__(self):
        self.js = js_files
        
    def __getitem__(self, item):
        try:
            return self.js[item]
        except KeyError:
            return default_js + ['split/common.js']

   
class webResources(object):
    
    def __init__(self, report, debug=False):
        self.css_resources = cssFiles()
        self.js_resources = jsFiles()
        self.debug = debug
        self.report = report
        self.css = self.css_link()
        self.js = self.js_link()
        
    def css_link(self):
        if self.debug:
            css_resource = self.get_all_css()
        else:
            status = concatenate_files(self.css_resources, self.report, "css")
            if status:
                css_file = "%s.css" % self.report
                css_resource = '''<link rel="stylesheet" href="css/%s" type="text/css" media="screen, projection">''' % css_file
            else:
                css_resource = self.get_all_css()
        return css_resource
    
    def get_all_css(self):
        resource_list = []
        for resource in self.css_resources[self.report]:
            css_link = '''<link rel="stylesheet" href="css/%s" type="text/css" media="screen, projection">''' % resource
            resource_list.append(css_link)
        css_resource = '\n'.join(resource_list)
        return css_resource
    
    def js_link(self):
        if self.debug:
            js_resource = self.get_all_js()
        else:
            status = concatenate_files(self.js_resources, self.report, "js")
            if status:
                js_file = "%s.js" % self.report
                js_resource = '''<script type="text/javascript" src="%s/js/%s"></script>''' % (config.db_url, js_file)
            else:
                js_resource = self.get_all_js()
        return js_resource
    
    def get_all_js(self):
        resource_list = []
        for resource in self.js_resources[self.report]:
            js_link = '''<script type="text/javascript" src="%s/js/%s"></script>''' % (config.db_url, resource)
            resource_list.append(js_link)
        js_resource = '\n'.join(resource_list)
        return js_resource 


def concatenate_files(resources, report, file_type):
    path = os.path.abspath(os.path.dirname(__file__)).replace('functions', '')
    filenames = [path + '/' + file_type + "/" + f for f in resources[report]]
    concat_file = path + "/" + file_type + "/" + report + "." + file_type
    status = True
    if not os.path.exists(concat_file):
        try:
            outfile = open(concat_file , 'w')
            for fname in filenames:
                infile = open(fname)
                outfile.write(infile.read())
                infile.close()
            outfile.close()
        except IOError:
            status = False
    return status
