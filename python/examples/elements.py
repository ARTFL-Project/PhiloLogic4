#!/usr/bin/env python
import philologic.shlaxtree as st
import sys
import codecs

for filename in sys.argv[1:]:
    file = codecs.open(filename,"r","utf-8")
    root = st.parse(file)
    header = root.find("teiHeader")
    print st.et.tostring(header)
    print header.findtext(".//titleStmt/title")
    print header.findtext(".//titleStmt/author")
