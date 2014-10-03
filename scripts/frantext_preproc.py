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
                 ".//sourceDesc/bibl/author[@type='marc100']",
                 ".//sourceDesc/bibl/author[@type='artfl']",
                 ".//sourceDesc/bibl/author/",
		 ".//titleStmt/author/", ## good 'un
		 ".//sourceDesc/biblStruct/monogr/author/name/",
                 ".//sourceDesc/biblFull/titleStmt/author/", ## good 'un
                 ".//sourceDesc/biblFull/titleStmt/respStmt/name/",
                 ".//sourceDesc/biblFull/titleStmt/author/",
                 ".//sourceDesc/bibl/titleStmt/author/"
                ],

                "title":
                [
                 ".//sourceDesc/bibl/title[@type='marc245']",
                 ".//sourceDesc/bibl/title[@type='artfl']",
                 ".//sourceDesc/bibl/title/",
		 ".//titleStmt/title/", ## good 'un
		 ".//sourceDesc/bibl/titleStmt/title/",
		 ".//sourceDesc/biblstruct/monogr/title/",
                 ".//sourceDesc/biblFull/titleStmt/title/"
                ],

                "author_dates":
                [
                 ".//sourceDesc/bibl/author/date/",
		 ".//titlestmt/author/date/"
                ],

                 "date":
                [
                 ".//profileDesc/creation/date/",
		 ".//fileDesc/sourceDesc/bibl/imprint/date/",
		 ".//sourceDesc/biblFull/publicationStmt/date/",
		 ".//publicationStmt/date/",
		 ".//sourceDesc/bibl/creation/date/", ## good 'un
		 ".//sourceDesc/bibl/date/", ## good 'un
                 ".//sourceDesc/bibl/imprint/date/",  ## good 'un
                 ".//sourceDesc/biblFull/publicationStmt/date/",
                 ".//profileDesc/dummy/creation/date/"
                ],

                "publisher":
                [
		 ".//sourceDesc/bibl/imprint[@type='marc534']",
		 ".//sourceDesc/bibl/imprint[@type='artfl']",
                 ".//sourceDesc/bibl/imprint/publisher",
		 ".//sourceDesc/biblstruct/monogr/imprint/publisher/name/",
		 ".//sourceDesc/biblfull/publicationstmt/publisher/",
		 ".//sourceDesc/bibl/publicationstmt/publisher/",
		 ".//sourceDesc/bibl/publisher/",
		 ".//publicationstmt/publisher/"
                ],

                "pub_place":
                [
                 ".//sourceDesc/bibl/imprint/pubPlace/",
                 ".//sourceDesc/biblStruct/monog/imprint/pubPlace/",
                 ".//sourceDesc/biblFull/publicationStmt/pubPlace/",
                 ".//sourceDesc/bibl/pubPlace/",
                 ".//sourceDesc/bibl/publicationStmt/pubPlace/"
                ],

                "pub_date":
                [
                 ".//sourceDesc/bibl/imprint/date/",
                 ".//sourceDesc/biblStruct/monog/imprint/date/",
                 ".//sourceDesc/biblFull/publicationStmt/date/",
                 ".//sourceDesc/bibFulll/imprint/date/",
                 ".//sourceDesc/bibl/date/",
                ],

		"extent":
		[
		".//sourceDesc/bibl/extent/",
		".//sourceDesc/biblStruct/monog//extent/",
		".//sourceDesc/biblFull/extent/",
		],

		"editor":
		[
		".//sourceDesc/bibl/editor/",
		".//sourceDesc/biblFull/titleStmt/editor/",
		".//sourceDesc/bibl/title/Stmt/editor/"
		],

		"identifiers":
		[
		".//publicationStmt/idno/"
		],

                "text_genre":
                [
                 ".//profileDesc/textClass/keywords[@scheme='genre']/term/"
                ],

                "keywords":
                [
                 ".//profileDesc/textClass/keywords/list/item/"
                ],

                "language":
                [
                 ".//profileDesc/langusage/language/"
                ],

                "notes":
                [
                 ".//fileDesc/notesStmt/note/",
                 ".//publicationStmt/notesStmt/note/"
                ],

                "auth_gender":
                [
                 ".//profileDesc/textClass/keywords[@scheme='authorgender']/term/"
                ],

                "collection":
                [
                 #".//sourceDesc/bibl/title[@type='artfl']",
		".//seriesStmt/title/"
                ],

                "period":
                [
                 ".//profileDesc/textClass/keywords[@scheme='period']/list/item/"
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
    ## getting rid of newlines and leftover CONVERT-TARGETs ##
    for field in out:
	if re.search("CONVERT-TARGET",out[field]):
		out[field] = ""
	if re.search("\n",out[field]):
		out[field] = re.sub("\n", " ",out[field])
		out[field] = re.sub("\s{2,}", " ",out[field])
    date = i["date"]
    date_m = re.search("[0-9]{3,4}",date)
    if date_m:
        out["date"] = date_m.group()
    
    return out

###################################
##                               ##
##    Main Loop                  ##
##                               ##
###################################

import os,sys,re
from elementtree import ElementTree as etree
#import xml.etree.ElementTree as etree

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
	#print data
	all_data.append(data)
    #print "sorting"
    all_data.sort(key=lambda d: (d['date'],d['author'],d['title'],d['filename'],d['text_genre'],d['auth_gender'],d['period'],d['publisher'],d['pub_place'],d['pub_date'],d['editor'],d['author_dates'],d['identifiers'],d['collection'],d['extent'],d['notes'],d['keywords']) )
#    for d in all_data:
#        print d['create_date'],d['author'],d['title'],d['filename']
    return all_data
#    print all_data
#    print "done"    
    
if __name__ == "__main__":
    all_data = make_load_metadata(sys.argv[1:])
    for d in all_data:                                                                                                                                                                                                               
        #print d['date'],d['author'],d['title'],d['text_genre'],d['auth_gender'],d['period'],d['publisher'],d['pub_place'],d['pub_date'],d['editor'],d['author_dates'],d['identifiers'],d['collection'],d['extent'],d['notes'],d['keywords'],d['filename']  
	print d['text_genre']
