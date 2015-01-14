#!/usr/bin/env python
import sys
import os
import subprocess
from datetime import datetime
import struct
import HitList
import re
import unicodedata
from QuerySyntax import parse_query, group_terms

def query(db,terms,corpus_file=None,corpus_size=0,method=None,method_arg=None,limit=3000,filename="", query_debug=False):
    sys.stdout.flush()
    tstart = datetime.now()

    parsed = parse_query(terms)
    grouped = group_terms(parsed)
    split = split_terms(grouped)

#    print >> sys.stderr, "QUERY FORMATTED at ", datetime.now() - tstart
    words_per_hit = len(split)
 #   print >> sys.stderr, "QUERY SPLIT at ", datetime.now() - tstart, repr(split)
    origpid = os.getpid()
    if not filename:
        hfile = str(origpid) + ".hitlist"
    dir = db.locals["db_path"] + "/hitlists/"
    filename = filename or (dir + hfile)
    hl = open(filename, "w")
    err = open("/dev/null", "w")
    freq_file = db.locals["db_path"]+"/frequencies/normalized_word_frequencies"
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
            print >> sys.stderr, "WORKER DETACHED at ", datetime.now() - tstart
            args = ["search4", db.path,"--limit",str(limit)]
            if corpus_file and corpus_size:
                args.extend(("--corpusfile", corpus_file , "--corpussize" , str(corpus_size)))
            if method and method_arg:
                args.extend((method,str(method_arg)))

            worker = subprocess.Popen(args,stdin=subprocess.PIPE,stdout=hl,stderr=err)
            print >> sys.stderr, "WORKER STARTED"
            if query_debug == True:
                print >> sys.stderr, "DEBUGGING"
                query_log_fh = filename + ".terms"
                print >> sys.stderr, "LOGGING to " + filename + ".terms"
                logger = subprocess.Popen(["tee",query_log_fh],stdin=subprocess.PIPE,stdout = worker.stdin)
                print >> sys.stderr, "EXPANDING"
                expand_query(split,freq_file,logger.stdin)
                logger.stdin.close()
            else:
                expand_query(split,freq_file,worker.stdin)

            worker.stdin.close()

            returncode = worker.wait()

            if returncode == -11:
                print >> sys.stderr, "SEGFAULT"
                seg_flag = open(filename + ".error","w")
                seg_flag.close()
            #do something to mark query as finished
            flag = open(filename + ".done","w")
            flag.write(" ".join(args) + "\n")
            flag.close()
#            print >> sys.stderr, "SUBPROC DONE at ", datetime.now() - tstart
            os._exit(0)
    else:
        hl.close()
        return HitList.HitList(filename,words_per_hit,db)

def split_terms(grouped):
    print >> sys.stderr, repr(grouped)
    split = []
    for group in grouped:
        if len(group) == 1:
            kind,token = group[0]
            if kind == "QUOTE" and token.find(" ") > 1: #we can split quotes on spaces if there is no OR
                for split_tok in token[1:-1].split(" "):
                    split.append( ( ("QUOTE",'"'+split_tok+'"' ), ) )
            elif kind == "RANGE":
                split.append( ( ("TERM",token), ) )
#                split_group = []
#                for split_tok in token.split("-"):
#                    split_group.append( ( ("TERM",split_tok), ) )
#                split.append(split_group)
            else:
                split.append(group)
        else:
            split.append(group)
    return split

def expand_query(split, freq_file, dest_fh):
    first = True
    grep_proc = None
    print >> sys.stderr, repr(split)
    for group in split:
        if first == True:
            first = False
        else: # bare newline starts a new group, except the first
            dest_fh.write("\n")
        # if we have multiple terms in the group, should check to make sure they don't repeat
        # if it's a single term, we can skip that
        if len(group) == 1: # if we have a one-token group, don't need to sort and uniq
            filters = subprocess.Popen("cut -f 2", stdin=subprocess.PIPE,stdout=dest_fh, shell=True)            
        else: # otherwise we need to merge the egrep results and remove duplicates.
            filters = subprocess.Popen("cut -f 2 | sort | uniq", stdin=subprocess.PIPE,stdout=dest_fh, shell=True)

        for kind,token in group: # or, splits, and ranges should have been taken care of by now.
            if kind == "TERM" or kind == "RANGE":
                grep_word(token,freq_file,filters.stdin)
            elif kind == "QUOTE":
                filters.stdin.write(token[1:-1] + "\n") 
            # what to do about NOT?
        filters.stdin.close()    
        filters.wait()
#    dest_fh.close()
    return filters

def grep_word(token,freq_file,dest_fh):
    print >> sys.stderr, "IN_GREP_WORD", repr(token)
    norm_tok_uni = token.decode("utf-8").lower()
    print >> sys.stderr, repr(norm_tok_uni)
    norm_tok_uni_chars = [i for i in unicodedata.normalize("NFKD",norm_tok_uni) if not unicodedata.combining(i)]
    print >> sys.stderr, repr(norm_tok_uni_chars)
#                norm_tok_uni_chars = [u"^"] + norm_tok_uni_chars + [u"\b"]
    norm_tok = u"".join(norm_tok_uni_chars).encode("utf-8")
    grep_command = ['egrep', '-i', '^%s[[:blank:]]' % norm_tok, '%s' % freq_file]
    print >> sys.stderr, "GREP_COMMAND", "".join(grep_command)
    print >> sys.stderr, repr(norm_tok)
    grep_proc = subprocess.Popen(grep_command,stdout=dest_fh)
    grep_proc.wait()    
    return grep_proc
