#!/usr/bin/env python
import sys
import time
import philologic.PhiloDB

db_path = sys.argv[1]
db = philologic.PhiloDB.PhiloDB(db_path,7)

print >> sys.stderr, "enter a full-text query.  like 'the stage|player'."
line = sys.stdin.readline()
q = db.query(line.strip())

while not q.done:
    time.sleep(.05)
    q.update() # have to check if the query is completed yet.

for hit in q:
    doc_id = q.get_doc(hit)
    offsets = q.get_bytes(hit)
    byte_offset = offsets[0]
    filename = db.toms[doc_id]["filename"]
    author = db.toms[doc_id]["author"]
    title = db.toms[doc_id]["title"]
    print "%s : %s,%s %s@%d" % (hit,author,title,filename,byte_offset)

    conc_start = byte_offset - 200
    if conc_start < 0: conc_start = 0
    text_path = db_path + "/TEXT/" + filename
    text_file = open(text_path)
    text_file.seek(conc_start)
    text = text_file.read(400)
    print text

hits = len(q)
print >> sys.stderr, "%d hits" % hits
