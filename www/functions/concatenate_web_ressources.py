#!/usr/bin/env python

import os.path
from web_config import WebConfig

theme = WebConfig().theme
report_files = {"css": {"landing_page": ["split/style.css", "split/searchForm.css", "split/landingPage.css", "split/%s" % theme],
                        "concordance": ["split/style.css", "split/searchForm.css", "split/concordanceKwic.css", "split/%s" % theme],
                        "kwic": ["split/style.css", "split/searchForm.css", "split/concordanceKwic.css", "split/%s" % theme],
                        "concordance_from_collocation": ["split/style.css", "split/searchForm.css", "split/concordanceKwic.css", "split/%s" % theme],
                        "bibliography": ["split/style.css", "split/searchForm.css", "split/concordanceKwic.css", "split/%s" % theme],
                        "collocation": ["split/style.css", "split/searchForm.css", "split/%s" % theme],
                        "time_series": ["split/style.css", "split/searchForm.css", "split/timeSeries.css", "split/%s" % theme],
                        "navigation": ["image_gallery/blueimp-gallery.min.css", "split/style.css", "split/searchForm.css", "split/textObjectNavigation.css", "split/%s" % theme],
                        "t_o_c": ["split/style.css", "split/searchForm.css", "split/textObjectNavigation.css", "split/%s" % theme]},
                "js": {"landing_page": ["split/common.js", "split/landingPage.js"],
                        "concordance": ["split/common.js", "plugins/jquery.slimscroll.min.js", "split/sidebar.js", "plugins/jquery.hoverIntent.minified.js", "split/concordanceKwic.js"],
                        "kwic": ["split/common.js", "plugins/jquery.slimscroll.min.js", "split/sidebar.js", "plugins/jquery.hoverIntent.minified.js", "split/concordanceKwic.js"],
                        "time_series": ["split/common.js", "split/timeSeries.js"],
                        "collocation": ["split/common.js", "plugins/jquery.tagcloud.js", "split/collocation.js"],
                        "ranked_relevance": ["split/common.js", "split/rankedRelevance.js"],
                        "bibliography": ["split/common.js", "plugins/jquery.slimscroll.min.js", "split/sidebar.js", "split/bibliography.js"],
                        "navigation": ["plugins/jquery.blueimp-gallery.min.js", "split/common.js", "plugins/jquery.scrollTo.min.js", "split/textObjectNavigation.js"],
                        "concordance_from_collocation": ["split/common.js", "split/concordanceFromCollocation.js"],
                        "t_o_c": ["split/common.js", "split/toc.js"],
                        "error": [],
                        "access": []}
                }

def concatenate_files(path, report, debug=False):
    path = os.path.abspath(os.path.dirname(__file__)).replace('functions', '')
    for file_type in ["css", "js"]:
        concat_file = path + "/" + file_type + "/" + report + "." + file_type
        if debug == True:
            write_file(path, concat_file, file_type, report) 
        elif not os.path.exists(concat_file):
            write_file(path, concat_file, file_type, report)
        else:
            pass
                        
def write_file(path, concat_file, file_type, report):
    filenames = [path + '/' + file_type + "/" + f for f in report_files[file_type][report]]
    with open(concat_file , 'w') as outfile:
        for fname in filenames:
            with open(fname) as infile:
                outfile.write(infile.read())