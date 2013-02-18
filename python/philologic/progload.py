#!/usr/bin/env python
import xml.parsers.expat
import re
import os
import sys
import codecs
import math
import cPickle
import AbstractParser4 as AbstractParser

#Initialize some globals
sortkeys = "-k 1,1 -k 2,2n -k 3,3n -k 4,4n -k 5,5n -k 6,6n -k 7,7n -k 8,8n" # gnu sort command-line option.  Don't alter.

blocksize = 2048 # index block size.  Don't alter.
index_cutoff = 10 # index frequency cutoff.  Don't. alter.

usage = "usage: progload.py destination_path texts ..."

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

#work out all the filenames beforehand.
fileinfo = [{"orig":os.path.abspath(x),
             "name":os.path.basename(x),
             "id":n + 1,
             "newpath":textdir + os.path.basename(x),
             "raw":workdir + os.path.basename(x) + ".raw",
             "words":workdir + os.path.basename(x) + ".words.sorted",
             "toms":workdir + os.path.basename(x) + ".toms",
             "sortedtoms":workdir + os.path.basename(x) + ".toms.sorted",
             "results":workdir + os.path.basename(x) + ".results"} for n,x in enumerate(texts)]

print "copying raw data into place..."
for t in fileinfo:
    os.system("cp %s %s" % (t["orig"],t["newpath"]))

#We'll define our parse routine here, then call it below in the fork loop.
def parsework(name,docid,path,raw,words,toms,sortedtoms,results):
        i = open(path)
        o = codecs.open(raw, "w", "utf-8")
        print "parsing %d : %s" % (docid,name)
        parser = AbstractParser.AbstractParser(name,docid)
        r = parser.parse(i,o)
        # parser.parse() writes a raw output stream to o.  returns a (maxobjects,counts) tuple.
        wordcommand = "cat %s | egrep \"^word \" | \
                       cut -d \" \" -f 2,3,4,5,6,7,8,9,10,11 | sort %s > %s" % (raw,sortkeys,words)
        os.system(wordcommand)
#        Toms.mktoms(open(raw),open(toms,"w")) # Toms should probably be utf-8.
        os.system("cat %s | egrep \"^doc|^div\" | sort -k 1,1n -k 2,2n -k 3,3n -k 4,4n -k 5,5n > %s" % (raw,sortedtoms))
        i.close()
        o.close()
        return r

print "parsing..."
max_workers = 8
total = len(texts)
if max_workers < 1:
    print usage
    exit() #should be less opaque here.  but someone must be screwing with us if we have < 1 workers allowed, right?
workers = 0
done = 0
omax = [0,0,0,0,0,0,0,0,0]
totalcounts = {}
procs = {}
filequeue = fileinfo[:]
reduce_queue = []

os.system("touch %s" % (workdir + "/words.sorted"))
os.system("touch %s" % (workdir + "/toms.sorted"))

#the main loop.  fork and parse up to n simultaneous workers.  tabulate results as they come in.
while done < total:
    while filequeue and workers < max_workers:
        # we want to have up to max_workers processes going at once.
        text = filequeue.pop(0) # parent and child will both know the relative filenames
        pid = os.fork()
        if pid: #the parent process tracks the child 
            procs[pid] = text.copy() # we need to know where to grab the results from.
            workers += 1
        if not pid: # the child process parses then exits.
            r = parsework(text["name"],text["id"],text["newpath"],text["raw"],text["words"],text["toms"],text["sortedtoms"],text["results"])
            rf = open(text["results"],"w")
            cPickle.dump(r,rf) # write the result out.
            rf.close()
            exit()
    #meanwhile, the parent waits for any child to exit.
    pid,status = os.waitpid(0,0) # this hangs until any one child finishes.  should check status for problems.
    done += 1 
    workers -= 1
    (vec,count_dict) = cPickle.load(open(procs[pid]["results"])) #load in the results from the child's parsework() function.
    #print vec
    omax = [max(x,y) for x,y in zip(vec,omax)]
    for word,freq in count_dict.items():
        totalcounts[word] = totalcounts.get(word,0) + freq
    # merge the results progressively. may make this it's own subprocess loop.
    print "merging %d..." % procs[pid]["id"]
    os.system("sort -m %s %s %s > %s" % (sortkeys,procs[pid]["words"], workdir + "/words.sorted", workdir + "/words.sorted.new") )
    os.system("sort -m -k 1,1n -k 2,2n -k 3,3n -k 4,4n %s %s > %s" % (procs[pid]["sortedtoms"], workdir + "/toms.sorted", workdir + "/toms.sorted.new") )
    print "moving ..."
    os.system("mv %s %s" % (workdir + "/words.sorted.new",workdir + "/words.sorted"))
    os.system("mv %s %s" % (workdir + "/toms.sorted.new",workdir + "/toms.sorted"))
    print "done."

print omax
print "%d total tokens in %d unique types." % (sum(x for x in totalcounts.values()),len(totalcounts.keys()))
print "parsed %d files successfully." % len(fileinfo)
    
#print "done sorting individual files.\nmerging... this can take a few minutes..."
#wordfilearg = " ".join(file["words"] for file in fileinfo)

#os.system("sort -m %s %s > %s" % (sortkeys,wordfilearg, workdir + "/all.words.sorted") )
#os.system("sort -m -k 1,1n -k 2,2n -k 3,3n -k 4,4n %s > %s" % (" ".join(file["sortedtoms"] for file in fileinfo), workdir + "/all.toms.sorted") )
print "done merging.\nnow analyzing for compression."

words = open(workdir + "/words.sorted")

# First we need to calculate the width of each numeric field in the index, by taking the log base 2 and rounding up.
vl = [max(int(math.ceil(math.log(float(x),2.0))),1) if x > 0 else 1 for x in omax]

print vl
width = sum(x for x in vl)
print str(width) + " bits wide."

hits_per_block = (blocksize * 8) // width #that's a hard integer division.  watch out for this in python-3.0
freq1 = index_cutoff
freq2 = 0
offset = 0

# now scan over the frequency table to figure out how wide the frequency fields are, and how large the block file will be.
for word,f in totalcounts.items():
    if f > freq2:
        freq2 = f
    if f < index_cutoff:
        pass # low-frequency words don't go into the block-mode index.
    else:
        blocks = 1 + f // (hits_per_block + 1) #high frequency words have at least one block.
        offset += blocks * blocksize

# take the log base 2 for the length of the binary representation.
freq1_l = math.ceil(math.log(float(freq1),2.0))
freq2_l = math.ceil(math.log(float(freq2),2.0))
offset_l = math.ceil(math.log(float(offset),2.0))

print "freq1: %d; %d bits" % (freq1,freq1_l)
print "freq2: %d; %d bits" % (freq2,freq2_l)
print "offst: %d; %d bits" % (offset,offset_l)

# now write it out in our legacy c-header-like format.  TODO: reasonable format, or ctypes bindings for packer.
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

print "analysis done.  packing index.  this can take a few minutes..."
os.system("pack4 " + workdir + "dbspecs4.h < " + workdir + "/words.sorted")

print "all indices built. moving into place."
os.system("mv index ../index")
os.system("mv index.1 ../index.1")
os.system("mv toms.sorted ../toms")
os.mkdir(destination + "/src/")
os.system("mv dbspecs4.h ../src/dbspecs4.h")
print "done."
