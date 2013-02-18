#!/usr/bin/env python 
import sys
import re
import time
import philologic.PhiloDB

if __name__ == "__main__":

    db_path = sys.argv[1]
    db = philologic.PhiloDB.PhiloDB(db_path,7)
    
    print >> sys.stderr, "enter a full-text query.  like 'the stage|player'."
    line = sys.stdin.readline()
    print "<frequency>"
    q = db.query(line.strip())
    
    authors = {}
    titles = {}
    
    while not q.done:
        time.sleep(.05)
        q.update() # have to check if the query is completed yet.
    
    for hit in q:
        byte_offset = hit[6]
        offsets = list(hit[6:])
        offsets.reverse()
        
        doc_id = hit[0]
        metadata = db.toms[doc_id]
        author = metadata["author"]
        title = metadata["title"]

        if author in authors:
            authors[author] += 1
        else:
            authors[author] = 1
        if title in titles:
            titles[title] += 1
        else:
            titles[title] = 1

    print "<category n='author'>"
    for n,f in authors.items():
        print "<label>%s</label>" % n
        print "<freq>%d</freq>" % f
    print "</category>"
    print "<category n='title'>"
    for n,f in titles.items():
        print "<label>%s</label>" % n
        print "<freq>%d</freq>" % f
    print "</category>"    
    print >> sys.stderr, "%d total occurences" % len(q)
    print "</frequency>"
