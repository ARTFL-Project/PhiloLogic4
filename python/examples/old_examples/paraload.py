#!/usr/bin/env python
import xml.parsers.expat
import re
import os
import sys
import codecs
import math
import multiprocessing
from philologic import OHCOVector,Toms,AbstractParser

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

pool = multiprocessing.Pool(8)

def parsework(docid,path,textdir,workdir,q):
        sortkeys = "-k 1,1 -k 2,2n -k 3,3n -k 4,4n -k 5,5n -k 6,6n -k 7,7n -k 8,8n"
#        (docid,path,textdir,workdir,q) = info
        f = open(path)
        filename = os.path.basename(path)
        origpath = os.path.abspath(path)
        newpath = textdir + filename
        os.system("cp %s %s" % (origpath, newpath))
        outpath = workdir + filename + ".raw"
        o = codecs.open(outpath, "w", "utf-8")
        print "parsing %d : %s" % (docid,filename)
        parser = AbstractParser.AbstractParser(filename,docid)
        r = parser.parse(f,o)
        wordcommand = "cat %s | egrep \"^word \" | cut -d \" \" -f 2,3,4,5,6,7,8,9,10,11 | sort %s > %s" % (outpath,sortkeys,workdir + filename + ".words.sorted")
        os.system(wordcommand)
        tomsfile = workdir + filename + ".toms"
        Toms.mktoms(open(outpath),open(tomsfile,"w"))
        sortedtomsfile = workdir + filename + ".toms.sorted"
        os.system("cat %s | sort -k 1,1n -k 2,2n -k 3,3n -k 4,4n -k 5,5n > %s" % (tomsfile,sortedtomsfile))
        q.put(r)
        sys.exit()

"parsing..."
max_workers = 8
count = len(texts)
if max_workers < 1:
    exit()
working = 0
done = 0
q = multiprocessing.Queue()
parselist = ((x[0],x[1],textdir,workdir,q) for x in enumerate(texts))
maxspecs = [0,0,0,0,0,0,0,0,0]
totalcounts = {}
while done < count:
    while working < max_workers and done + working < count:
        p = multiprocessing.Process(target=parsework,args=parselist.next())
        p.start()
        working += 1
    i = q.get()
    specs,counts = i
    maxspecs = [max(x,y) for x,y in zip(specs,maxspecs)]
    for word,wordcount in counts.items():
        totalcounts[word] = totalcounts.get(word,0) + wordcount
    working -= 1
    done += 1

fileinfo = [{"name":x,
             "path":os.path.basename(x),
             "raw":workdir + os.path.basename(x) + ".raw",
             "words":workdir + os.path.basename(x) + ".words.sorted",
             "toms":workdir + os.path.basename(x) + ".toms",
             "sortedtoms":workdir + os.path.basename(x) + ".toms.sorted"} for x in texts]

print maxspecs
print "%d total tokens in %d unique types." % (sum(x for x in totalcounts.values()),len(totalcounts.keys()))
print "parsed %d files successfully.\nsorting..." % len(fileinfo)
    
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
