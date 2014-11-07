#!/usr/bin/env python

import os.path
from web_config import WebConfig

config = WebConfig()
theme = config.theme

css_files = {"landing_page": ["split/style.css", "split/searchForm.css", "split/landingPage.css", "split/%s" % theme],
            "concordance": ["split/style.css", "split/searchForm.css", "split/concordanceKwic.css", "split/%s" % theme],
            "kwic": ["split/style.css", "split/searchForm.css", "split/concordanceKwic.css", "split/%s" % theme],
            "concordance_from_collocation": ["split/style.css", "split/searchForm.css", "split/concordanceKwic.css", "split/%s" % theme],
            "bibliography": ["split/style.css", "split/searchForm.css", "split/concordanceKwic.css", "split/%s" % theme],
            "collocation": ["split/style.css", "split/searchForm.css", "split/%s" % theme],
            "time_series": ["split/style.css", "split/searchForm.css", "split/timeSeries.css", "split/%s" % theme],
            "navigation": ["image_gallery/blueimp-gallery.min.css", "split/style.css", "split/searchForm.css", "split/textObjectNavigation.css", "split/%s" % theme],
            "t_o_c": ["split/style.css", "split/searchForm.css", "split/textObjectNavigation.css", "split/%s" % theme]}

default_js = ['bootstrap/bootstrap.min.js', "plugins/jquery.history.js", "plugins/velocity.min.js", "plugins/velocity.ui.min.js", "plugins/jquery-ui.min.js"]
js_files = {"landing_page": default_js + ["split/common.js", "split/landingPage.js"],
            "concordance": default_js + ["split/common.js", "plugins/jquery.slimscroll.min.js", "split/sidebar.js", "plugins/jquery.hoverIntent.minified.js", "split/concordanceKwic.js"],
            "kwic": default_js + ["split/common.js", "plugins/jquery.slimscroll.min.js", "split/sidebar.js", "plugins/jquery.hoverIntent.minified.js", "split/concordanceKwic.js"],
            "time_series": default_js +["split/common.js", "split/timeSeries.js"],
            "collocation": default_js + ["split/common.js", "plugins/jquery.tagcloud.js", "split/collocation.js"],
            "ranked_relevance": default_js + ["split/common.js", "split/rankedRelevance.js"],
            "bibliography": default_js + ["split/common.js", "plugins/jquery.slimscroll.min.js", "split/sidebar.js", "split/bibliography.js"],
            "navigation": default_js + ["plugins/jquery.blueimp-gallery.min.js", "split/common.js", "plugins/jquery.scrollTo.min.js", "split/textObjectNavigation.js"],
            "concordance_from_collocation": default_js + ["split/common.js", "split/concordanceFromCollocation.js"],
            "t_o_c": default_js + ["split/common.js", "split/toc.js"],
            "error": default_js,
            "access": default_js}


class cssFiles(object):
    
    def __init__(self):
        self.css = css_files
        
    def __getitem__(self, item):
        try:
            return self.css[item]
        except KeyError:
            return self.css["concordance"]


class jsFiles(object):
    
    def __init__(self):
        self.js = js_files
        
    def __getitem__(self, item):
        try:
            return self.js[item]
        except KeyError:
            return self.js["concordance"]

   
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
                css_resource = '''<link rel="stylesheet" href="%s/css/%s" type="text/css" media="screen, projection">''' % (config.db_url, css_file)
            else:
                css_resource = self.get_all_css()
        return css_resource
    
    def get_all_css(self):
        resource_list = []
        for resource in self.css_resources[self.report]:
            css_link = '''<link rel="stylesheet" href="%s/css/%s" type="text/css" media="screen, projection">''' % (config.db_url, resource)
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