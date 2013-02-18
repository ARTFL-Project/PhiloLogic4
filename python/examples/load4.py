#!/usr/bin/env python
import xml.parsers.expat
import re
import os
import sys
import codecs
import math
from philologic import OHCOVector,Toms,TEIParser

#Initialize some globals
sortkeys = "-k 1,1 -k 2,2n -k 3,3n -k 4,4n -k 5,5n -k 6,6n -k 7,7n -k 8,8n"
blocksize = 2048
index_cutoff = 10

usage = "usage: load4 destination_path texts ..."

try :
    destination = sys.argv[1]
except IndexError:
    print usage
    exit()

print "setting up directory in " + destination

os.mkdir(destination)
workdir = destination + "/WORK/"
textdir = destination + "/TEXT/"
os.mkdir(workdir)
os.mkdir(textdir)
os.chdir(workdir)

texts = sys.argv[2:]
if not sys.argv[2:]:
    print usage
    exit()

fileinfo = []

"parsing..."
for docid,file in enumerate(texts): 
    f = open(file)
    filename = os.path.basename(file)
    origpath = os.path.abspath(file)
    path = textdir + filename
    os.system("cp %s %s" % (origpath, path))
    outpath = workdir + filename + ".raw"
    o = codecs.open(outpath, "w", "utf-8")
    print "parsing %s @ %s" % (filename,origpath)
    parser = TEIParser.TEIParser(filename,docid)
    parser.parse(f,o)
    fileinfo.append({"path":path,"name":filename,"raw":outpath})

print "parsed %d files successfully.\nsorting..." % len(fileinfo)
for file in fileinfo:
    print "sorting %s" % file["name"]
    file["words"] = file["path"] + ".words.sorted"
    wordcommand = "cat %s | egrep \"^word \" | cut -d \" \" -f 2,3,4,5,6,7,8,9,10,11 | sort %s > %s" % (file["raw"],sortkeys,file["words"] )
    os.system(wordcommand)

for file in fileinfo:
    print "building metadata for %s" % file["name"]
    file["toms"] = file["path"] + ".toms"
    Toms.mktoms(open(file["raw"],"r"),open(file["toms"],"w"))
    file["sortedtoms"] = file["path"] + ".toms.sorted"
    tomscommand = "cat %s | sort -k 1,1n -k 2,2n -k 3,3n -k 4,4n -k 5,5n > %s" % (file["toms"],file["sortedtoms"])
    os.system(tomscommand)
    
print "done sorting individual files.\nmerging..."
wordfilearg = " ".join(file["words"] for file in fileinfo)

os.system("sort -m %s %s > %s" % (sortkeys,wordfilearg, workdir + "/all.words.sorted") )
os.system("sort -m -k 1,1n -k 2,2n -k 3,3n -k 4,4n %s > %s" % (" ".join(file["sortedtoms"] for file in fileinfo), workdir + "/all.toms.sorted") )
print "done merging.\nnow analyzing for compression...."

words = open(workdir + "/all.words.sorted")
testline = words.readline()
v = [0 for i in testline.split(" ")[1:]]
count = 0
freq = {}
word = ""
words.seek(0)
for line in words:
    count += 1
    word = line.split(" ")[0]
    try:
        freq[word] += 1
    except KeyError:
        freq[word] = 1
    fields = [int(i) for i in line.split(" ")[1:]]
    v = [i if i > v[e] else v[e] for e,i in enumerate(fields)]

print str(count) + " words total." 
print v

vl = [max(int(math.ceil(math.log(float(x),2.0))),1) if x > 0 else 1 for x in v]

print vl
width = sum(x for x in vl)
print str(width) + " bits wide."

hits_per_block = (blocksize * 8) // width
freq1 = index_cutoff
freq2 = 0
offset = 0

for word,f in freq.items():
    if f > freq2:
        freq2 = f
    if f < index_cutoff:
        pass
    else:
        blocks = 1 + f // (hits_per_block + 1)
        offset += blocks * blocksize

freq1_l = math.ceil(math.log(float(freq1),2.0))
freq2_l = math.ceil(math.log(float(freq2),2.0))
offset_l = math.ceil(math.log(float(offset),2.0))

print "freq1: %d; %d bits" % (freq1,freq1_l)
print "freq2: %d; %d bits" % (freq2,freq2_l)
print "offst: %d; %d bits" % (offset,offset_l)

dbs = open(workdir + "dbspecs4.h","w")
print >> dbs, "#define FIELDS 9"
print >> dbs, "#define TYPE_LENGTH 1"
print >> dbs, "#define BLK_SIZE " + str(blocksize)
print >> dbs, "#define FREQ1_LENGTH " + str(freq1_l)
print >> dbs, "#define FREQ2_LENGTH " + str(freq2_l)
print >> dbs, "#define OFFST_LENGTH " + str(offset_l)
print >> dbs, "#define NEGATIVES {0,0,0,0,0,0,0,0,0}"
print >> dbs, "#define DEPENDENCIES {-1,0,1,2,3,4,5,0,0}"
print >> dbs, "#define BITLENGTHS {%s}" % ",".join(str(i) for i in vl)
dbs.close()

print "analysis done.  packing index."
os.system("pack4 " + workdir + "dbspecs4.h < " + workdir + "/all.words.sorted")

print "all indices built. moving into place."
os.system("mv index ../index")
os.system("mv index.1 ../index.1")
os.system("mv all.toms.sorted ../toms")
os.mkdir(destination + "/src/")
os.system("mv dbspecs4.h ../src/dbspecs4.h")
print "done."