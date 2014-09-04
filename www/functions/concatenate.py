#!/usr/bin/env python

import os.path

report_files = {"css": {"landing_page": ["split/style.css", "split/searchForm.css"],
                        "concordance": ["split/style.css", "split/searchForm.css", "split/concordanceKwic.css"],
                        "kwic": ["split/style.css", "split/searchForm.css", "split/concordanceKwic.css"],
                        "concordance_from_collocation": ["split/style.css", "split/searchForm.css", "split/concordanceKwic.css"],
                        "bibliography": ["split/style.css", "split/searchForm.css", "split/concordanceKwic.css"],
                        "collocation": ["split/style.css", "split/searchForm.css"],
                        "time_series": ["split/style.css", "split/searchForm.css", "split/timeSeries.css"],
                        "navigation": ["split/style.css", "split/searchForm.css", "split/textObjectNavigation.css"],
                        "t_o_c": ["split/style.css", "split/searchForm.css", "split/textObjectNavigation.css"]},
                "js": {"landing_page": ["split/common.js"],
                        "concordance": ["split/common.js", "plugins/jquery.slimscroll.min.js", "split/sidebar.js", "plugins/jquery.hoverIntent.minified.js", "split/concordanceKwic.js"],
                        "kwic": ["split/common.js", "plugins/jquery.slimscroll.min.js", "split/sidebar.js", "plugins/jquery.hoverIntent.minified.js", "split/concordanceKwic.js"],
                        "time_series": ["split/common.js", "split/timeSeries.js"],
                        "collocation": ["split/common.js", "plugins/jquery.tagcloud.js", "split/collocation.js"],
                        "ranked_relevance": ["split/common.js", "split/rankedRelevance.js"],
                        "bibliography": ["split/common.js", "plugins/jquery.slimscroll.min.js", "split/sidebar.js", "split/bibliography.js"],
                        "navigation": ["split/common.js", "plugins/jquery.scrollTo.min.js", "split/textObjectNavigation.js"],
                        "concordance_from_collocation": ["split/common.js", "split/concordanceFromCollocation.js"],
                        "t_o_c": ["split/common.js", "split/toc.js"],
                        "error": [],
                        "access": []}
                }

def concatenate_files(path, report, debug=False):
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