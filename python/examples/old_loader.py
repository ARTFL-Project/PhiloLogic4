#!/usr/bin/env python
import re
import os
import sys
import codecs
import math
import cPickle
from philologic import OHCOVector,SqlToms,Parser

Parser = Parser.Parser

#Initialize some globals

sort_by_word = "-k 2,2"
sort_by_id = "-k 3,3n -k 4,4n -k 5,5n -k 6,6n -k 7,7n -k 8,8n -k 9,9n"

blocksize = 2048 # index block size.  Don't alter.
index_cutoff = 10 # index frequency cutoff.  Don't. alter.

os.environ["LC_ALL"] = "C" # Exceedingly important to get uniform sort order.
os.environ["PYTHONIOENCODING"] = "utf-8"

usage = "usage: forkload.py destination_path texts ..."

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
             "count":workdir + os.path.basename(x) + ".count",
             "results":workdir + os.path.basename(x) + ".results"} for n,x in enumerate(texts)]

print "copying raw data into place..."
for t in fileinfo:
    os.system("cp %s %s" % (t["orig"],t["newpath"]))

os.chdir(workdir)

#We'll define our parse routine here, then call it below in the fork loop.
def parsework(name,docid,path,raw,words,toms,sortedtoms,results,count):
    i = codecs.open(path,"r",)
    o = codecs.open(raw, "w",) # only print out raw utf-8, so we don't need a codec layer now.
    print "parsing %d : %s" % (docid,name)
    parser = Parser({"filename":name},docid,output=o)
    r = parser.parse(i)
    i.close()
    o.close()

    wordcommand = "cat %s | egrep \"^word\" | sort %s %s > %s" % (raw,sort_by_word,sort_by_id,words)
    os.system(wordcommand)

    countcommand = "cat %s | wc -l > %s" % (words,count)
    os.system(countcommand)

    tomscommand = "cat %s | egrep \"^doc|^div\" | sort %s > %s" % (raw,sort_by_id,sortedtoms)
    os.system(tomscommand)
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

#the main loop.  fork and parse up to n simultaneous workers.  tabulate results as they come in.
while done < total:
    while filequeue and workers < max_workers:
        # we want to have up to max_workers processes going at once.
        text = filequeue.pop(0) # parent and child will both know the relative filenames
        pid = os.fork()
        if pid: #the parent process tracks the child 
            procs[pid] = text["results"] # we need to know where to grab the results from.
            workers += 1
        if not pid: # the child process parses then exits.
            r = parsework(text["name"],text["id"],text["newpath"],text["raw"],text["words"],text["toms"],text["sortedtoms"],text["results"],text["count"])
            rf = open(text["results"],"w")
            cPickle.dump(r,rf) # write the result out.
            rf.close()
            exit()
    #meanwhile, the parent waits for any child to exit.
    pid,status = os.waitpid(0,0) # this hangs until any one child finishes.  should check status for problems.
    done += 1 
    workers -= 1
    vec = cPickle.load(open(procs[pid])) #load in the results from the child's parsework() function.
    #print vec
    omax = [max(x,y) for x,y in zip(vec,omax)]

print omax
print "parsed %d files successfully." % len(fileinfo)
    
print "done sorting individual files.\nmerging... this can take a few minutes..."
wordfilearg = " ".join(file["words"] for file in fileinfo)
words_result = workdir + "all.words.sorted"
tomsfilearg = " ".join(file["sortedtoms"] for file in fileinfo)
toms_result = workdir + "all.toms.sorted"
os.system("sort -m %s %s %s > %s" % (wordfilearg,sort_by_word,sort_by_id, workdir + "all.words.sorted") )
os.system("sort -m %s %s > %s" % (tomsfilearg,sort_by_id, workdir + "all.toms.sorted") )
print "done merging.\nnow analyzing for compression."

# First we need to calculate the width of each numeric field in the index, by taking the log base 2 and rounding up.
vl = [max(int(math.ceil(math.log(float(x),2.0))),1) if x > 0 else 1 for x in omax]

print vl
width = sum(x for x in vl)
print str(width) + " bits wide."

hits_per_block = (blocksize * 8) // width 
freq1 = index_cutoff
freq2 = 0
offset = 0

# unix one-liner for a frequency table
os.system("cut -f 2 %s | uniq -c | sort -rn -k 1,1> %s" % ( workdir + "/all.words.sorted", workdir + "/all.frequencies") )

# now scan over the frequency table to figure out how wide (in bits) the frequency fields are, and how large the block file will be.
for line in open(workdir + "/all.frequencies"):    
    f, word = line.rsplit(" ",1) # uniq -c pads output on the left side, so we split on the right.
    f = int(f)    
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

#print "STOP."
#sys.exit()
os.system("pack4 " + workdir + "dbspecs4.h < " + workdir + "/all.words.sorted")

print "all indices built. moving into place."
os.system("mv index ../index")
os.system("mv index.1 ../index.1")
#os.system("mv all.toms.sorted ../toms")
print "building metadata db."
toms = SqlToms.SqlToms("../toms.db",7)
toms.mktoms_sql(workdir + "/all.toms.sorted")
toms.dbh.execute("ALTER TABLE toms ADD COLUMN word_count;")
for f in fileinfo:
	count = int(open(f["count"]).read())
	toms.dbh.execute("UPDATE toms SET word_count = %d WHERE filename = '%s';" % (count,f["name"]))
toms.dbh.commit()
os.mkdir(destination + "/src/")
os.system("mv dbspecs4.h ../src/dbspecs4.h")
print "done."
