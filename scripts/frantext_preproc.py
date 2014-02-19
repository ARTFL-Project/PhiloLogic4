#!/usr/bin/env python

import philologic.shlaxtree as st
import codecs
import sys
import re
import string


###################################
##				 ##
##    The Paths			 ##
##				 ##
##				 ##
## These xpaths can be		 ## 
## customized and configured	 ##
## till the cows come home.	 ##
##				 ##
## This dict is used in the	 ##
## extract/extract_metadata	 ##
## functions.			 ##
##				 ##
## For fault tolerance:		 ##
## the format for these xpaths   ##
## should be all lowercase. Call ##
## me jaded and paranoid, but I  ##
## (CMC) do not even remotely	 ##
## trust that headers will ever	 ##
## conform to a single format.	 ##
##				 ##
## Might include a loop in the	 ##
## extract function to ensure	 ##
## the format.			 ##
##				 ##
################################### 

metadata_xpaths = {}

metadata_xpaths = {"author":
                [
                 ".//titleStmt/author/", ## good 'un                                                                                                                                                                                  
                 ".//sourceDesc/bibl/author/",
                 ".//publicationStmt/sourceDesc/bibl/author/",
                 ".//sourceDesc/bibl/author/",
                 ".//sourceDesc/bibl/author[@type='artfl']",
                 ".//sourceDesc/bibl/author[@type='marc100']",
                 ".//sourceDesc/biblStruct/monogr/author/name/",
                 ".//sourceDesc/biblFull/titleStmt/author/", ## good 'un                                                                                                                                                              
                 ".//sourceDesc/biblFull/titleStmt/respStmt/name/",
                 ".//sourceDesc/biblFull/titleStmt/author/",
                 ".//sourceDesc/bibl/titleStmt/author/"
                ],

                "title":
                [
                 ".//titleStmt/title/", ## good 'un                                                                                                                                                                                   
                 ".//titleStmt/title[@type='245'][@i2='2']",
                 ".//titleStmt/title[@type='artfl']",
                 ".//sourceDesc/bibl/title/",
                 ".//sourceDesc/bibl/titleStmt/title/",
                 ".//sourceDesc/biblFull/titleStmt/title[@type='245'][@i2='2']"
                 ".//sourceDesc/bibl/titleStmt/title/",
                 ".//sourceDesc/biblstruct/monogr/title/",
                 ".//sourceDesc/biblFull/titleStmt/title/"
                ],

                "author_dates":
                [
                 ".//sourceDesc/bibl/author/date/",
                 ".//titleStmt/author/date/"
                ],

                   "create_date":
                       [
                 ".//profileDesc/creation/date/",
                 ".//sourceDesc/bibl/date/", ## good 'un                                                                                                                                                                              
                 ".//sourceDesc/biblFull/publicationStmt/date/", ## good 'un                                                                                                                                                          
                 ".//publicationStmt/date/", ## good 'un                                                                                                                                                                              
                 ".//sourceDesc/bibl/creation/date/", ## good 'un                                                                                                                                                                     
                 ".//sourceDesc/bibl/imprint/date/",  ## good 'un                                                                                                                                                                     
                 ".//sourceDesc/biblFull/publicationStmt/date/",
                 ".//profileDesc/dummy/creation/date/"
                ],

                "publisher":
                [
                 ".//publicationStmt/publisher",
                 ".//sourceDesc/bibl/imprint/publisher",
                 ".//sourceDesc/biblFull/publicationStmt/publisher",
                 ".//sourceDesc/bibl/imprinttypeartfl/",
                 ".//sourceDesc/biblstruct/monogr/imprint/publisher/name/",
                 ".//sourceDesc/biblFull/titleStmt/publicationStmt/publisher/",
                 ".//sourceDesc/bibl/publicationStmt/publisher/",
                 ".//sourceDesc/bibl/publisher/"
                ],
                "pub_place":
                [
                 ".//publicationStmt/pubPlace/",
                 ".//publicationStmt/sourceDesc/bibl/imprint/pubPlace/",
                 ".//sourceDesc/biblFull/publicationStmt/pubPlace/",
                 ".//sourceDesc/bibl/imprint/pubPlace/",
                 ".//sourceDesc/biblstruct/monogr/imprint/pubPlace/",
                 ".//sourceDesc/biblFull/publicationStmt/pubPlace/",
                 ".//sourceDesc/biblFull/titleStmt/publicationStmt/pubPlace/",
                 ".//sourceDesc/bibl/pubPlace/",
                 ".//sourceDesc/bibl/publicationStmt/pubPlace/",
                 ".//publicationStmt/pubAddress/"
                ],

                "text_genre":
                [
                 ".//profileDesc/textClass/keywords[@scheme='genre']/term/"
                ],

                "auth_gender":
                [
                 ".//profileDesc/textClass/keywords[@scheme='authorgender']/term/"
                ],

                "text_form":
                [
                 ".//profileDesc/textClass/keywords[@scheme='form']/term/"
                ]

               }

###################################
##                               ##
## clean_up			 ##
##                               ##
## called from main loop.	 ##
##                               ##
## Preparing bib fields for	 ##
## display and, esp, cleaning	 ##
## dates for sorting.		 ##
##                               ##
###################################

def clean_up(i):
    out = dict(i)
    date = i["create_date"]
    date_m = re.search("[0-9]{3,4}",date)
    if date_m:
        out["create_date"] = date_m.group()
    
    return out

###################################
##                               ##
##    Main Loop                  ##
##                               ##
###################################

import os,sys,re
from elementtree import ElementTree as etree

def get_header(fn):
        fh = open(fn)
	header = ""
        while True:
            line = fh.readline()
            scan = re.search("<teiheader>|<temphead>",line,re.IGNORECASE)
            if scan:
                header = line[scan.start():]
                break
        while True:        
            line = fh.readline()
            scan = re.search("</teiheader>|<\/?temphead>", line, re.IGNORECASE)
            if scan:
                header = header + line[:scan.end()]
                break
            else:
                header = header + line
        tree = etree.fromstring(header)
	return(tree)

def make_load_metadata(filenames,prefix=""):
    all_data = []
    for i,fn in enumerate(filenames):
        tree = get_header(prefix+fn)
	data = {"filename":fn}
#	print i,fn,tree
	for field,paths in metadata_xpaths.items():
	   for path in paths:
		el = tree.find(path)
		if el is not None and el.text is not None:
			data[field] = el.text.encode("utf-8")
			break
	   if field not in data:
		data[field] = ""
	data = clean_up(data)
#	print data
	all_data.append(data)
#    print "sorting"
    all_data.sort(key=lambda d: (d['create_date'],d['author'],d['title'],d['filename']) )
#    for d in all_data:
#        print d['create_date'],d['author'],d['title'],d['filename']
    return all_data
#    print all_data
#    print "done"    
    
if __name__ == "__main__":
    all_data = make_load_metadata(sys.argv[1:])
    for d in all_data:                                                                                                                                                                                                               
        print d['create_date'],d['author'],d['title'],d['filename']   
