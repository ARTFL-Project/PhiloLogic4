#!/usr/bin/env python

import philologic.shlaxtree as st
import codecs
import sys
import re


###################################
##				 ##
##    The Paths			 ##
##				 ##
###################################

bib_metadata = {}

bib_metadata = {"auth_name":
		[".//sourceDesc/bibl/author[@type='marc100']",
		 ".//titleStmt/author",
		 ".//titleStmt/author/name/",
		 ".//sourceDesc/bibl/author/",
		 ".//sourceDesc/biblstruct/monogr/author/name/",
		 ".//sourceDesc/biblFull/titleStmt/respStmt/name/",
		 ".//sourceDesc/biblFull/titleStmt/author/",
		 ".//sourceDesc/bibl/titleStmt/author/"
		],

		"titles":
		[".//titleStmt/title/",
		 ".//sourceDesc/bibl/title/",
		 ".//sourceDesc/bibl/titleStmt/title/",
		 ".//sourceDesc/biblStruct/monogr/title/",
		 ".//sourceDesc/biblFull/titleStmt/title/"
		],

		"auth_dates":
		[".//sourceDesc/bibl/author/date/",
		 ".//titleStmt/author/date/"
		],

		"createdate":
		[".//profileDesc/creation/date",
		 ".//profileDesc/dummy/creation/date"
		],

		"publishers":
		[".//sourceDesc/bibl/imprinttypeartfl/",
		 ".//sourceDesc/bibl/imprint/publisher/",
		 ".//sourceDesc/biblStruct/monogr/imprint/publisher/name/",
		 ".//sourceDesc/biblFull/titleStmt/publicationStmt/publisher/",
		 ".//sourceDesc/biblFull/publicationStmt/publisher/",
		 ".//sourceDesc/bibl/publicationStmt/publisher/",
		 ".//sourceDesc/bibl/publisher/"
		],

		"pub_places":
		[".//sourceDesc/bibl/imprint/pubPlace/",
		 ".//sourceDesc/biblStruct/monogr/imprint/pubPlace/",
		 ".//sourceDesc/biblFull/publicationStmt/pubPlace/",
		 ".//sourceDesc/biblFull/titleStmt/publicationStmt/pubPlace/",
		 ".//sourceDesc/bibl/pubPlace/",
		 ".//sourceDesc/bibl/publicationStmt/pubPlace/",
		 ".//publicationStmt/pubAddress/"
		],

		"text_genre":
		[".//profileDesc/textClass/keywords[@scheme='genre']/term/",
		],

		"auth_gender":
		[".//profileDesc/textClass/keywords[@scheme='authorgender']/term/",
		],

		"text_form":
		[".//profileDesc/textClass/keywords[@scheme='form']/term/",
		]

	       }

###################################
##                               ##
##    Extract Loop               ##
##                               ##
###################################


def extract(filename,text):
    biblio = {}
    root = st.parse(text)
    header = root.find("teiHeader")
    
    biblio["filename"] = filename    

    for author in bib_metadata["auth_name"]:
	if header.findtext(author):
	    biblio["author"] = header.findtext(author)
	    break

    for auth_date in bib_metadata["auth_dates"]:
	if header.findtext(auth_date):
	    biblio["auth_date"] = header.findtext(auth_date)
	    break

    for gender in bib_metadata["auth_gender"]:
        if header.findtext(gender):
            biblio["gender"] = header.findtext(gender)
            break

    for title in bib_metadata["titles"]:
	if header.findtext(title):
	    biblio["title"] = header.findtext(title)
	    break

    for cr_date in bib_metadata["createdate"]:
	if header.findtext(cr_date):
	    biblio["date"] = int(header.findtext(cr_date))
	    break

    for genre in bib_metadata["text_genre"]:
	if header.findtext(genre):
	    biblio["genre"] = header.findtext(genre)
	    break

    for publisher in bib_metadata["publishers"]:
        if header.findtext(publisher):
            biblio["publisher"] = header.findtext(publisher)
            break

    for pub_place in bib_metadata["pub_places"]:
        if header.findtext(pub_place):
            biblio["pub_place"] = header.findtext(pub_place)
            break

    return biblio

###################################
##                               ##
##    Main Loop                  ##
##                               ##
###################################

if __name__ == "__main__":

    outbib = []
    
    for filename in sys.argv[1:]:
        header = []
        text = codecs.open(filename,"r","utf-8")
        text.readline()
        for line in text:
            if re.match("</teiHeader>",line):
                break
            else:
                header.append(line)
        record = extract(filename,header) 
        outbib.append(record)
    
    for record in sorted(outbib, key=lambda x:(x["date"], x["author"], x["title"])):
        print record 
