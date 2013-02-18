#!/usr/bin/env python
import sys
import os
import subprocess
import time
import struct
import HitList
import re

def query(db,terms,corpus_file=None,corpus_size=0,method=None,method_arg=None,limit=3000,filename=""):
    sys.stdout.flush()
    expandedterms = format_query(terms)
    words_per_hit = len(terms.split(" "))
    origpid = os.getpid()
    if not filename:
        hfile = str(origpid) + ".hitlist"
    dir = "/var/lib/philologic/hitlists/"
    filename = filename or (dir + hfile)
    hl = open(filename, "w")
    err = open("/dev/null", "w")
    pid = os.fork()
    if pid == 0:
        os.umask(0)
        os.chdir(dir)
        os.setsid()
        pid = os.fork()
        if pid > 0:
            os._exit(0)
        else:
            #now we're detached from the parent, and can do our work.
            args = ["search4", db,"--limit",str(limit)]
            if corpus_file and corpus_size:
                args.extend(("--corpusfile", corpus_file , "--corpussize" , str(corpus_size)))
            if method and method_arg:
                args.extend((method,str(method_arg)))
            worker = subprocess.Popen(args,stdin=subprocess.PIPE,stdout=hl,stderr=err)
            worker.communicate(format_query(terms))
            worker.stdin.close()
            worker.wait()
            #do something to mark query as finished
            flag = open(filename + ".done","w")
            flag.write(" ".join(args) + "\n")
            flag.close()
            os._exit(0)
    else:
        hl.close()
        return HitList.HitList(filename,words_per_hit,db)

def format_query(qstring):
    q = [level.split("|") for level in qstring.split(" ") ]
    qs = ""
    for level in q:
        for token in level:
            qs += token + "\n"
        qs += "\n"
    qs = qs[:-1] # to trim off the last newline.  just a quirk of the language.
    return qs
    
def get_context(file,offset,file_length,width,f):
    lo = max(0,offset - width)
    breakpoint = offset - lo
    ro = min(file_length, offset + width)

    fh = open(file)
    fh.seek(lo)
    buf = fh.read(ro - lo)
    lbuf = buf[:breakpoint]
    rbuf = buf[breakpoint:]
    (word,rbuf) = re.split("[\s.;:,<>?!]",rbuf,1)
    fh.close()    

    return f.format(lbuf + "<span rend=\"preserve\" style=\"color:red\"> " + word + "</span> " + rbuf)
    
def get_object(file,start,end):
    fh = open(file)
    fh.seek(start)
    buf = fh.read(end - start)
    fh.close()
    return buf
