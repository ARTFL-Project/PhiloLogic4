#!/usr/bin/env python
import sys
import os
import subprocess
import time
import struct
import HitList
import re
import unicodedata
from MetadataQuery import patterns
from QuerySyntax import parse_query

def query(db,terms,corpus_file=None,corpus_size=0,method=None,method_arg=None,limit=3000,filename=""):
    sys.stdout.flush()
    expandedterms = format_query(terms,db)
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
            args = ["search4", db.path,"--limit",str(limit)]
            if corpus_file and corpus_size:
                args.extend(("--corpusfile", corpus_file , "--corpussize" , str(corpus_size)))
            if method and method_arg:
                args.extend((method,str(method_arg)))
            worker = subprocess.Popen(args,stdin=subprocess.PIPE,stdout=hl,stderr=err)
            worker.communicate(format_query(terms,db))
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

def format_parsed_query(parsed_split,db):
    command = ""
    clauses = [[]]
    prior_label = "OR"
#        print parsed_split
    for label, token in parsed_split:
        if label == "QUOTE_S":
            if prior_label != "OR":
                clauses.append([])
                command += "\n"
            subtokens = token.split(" ")
            clauses[-1] += subtokens
            command += "\n".join(subt+"\n" for subt in subtokens)
        elif label == "TERM":
            if prior_label != "OR":
                clauses.append([])
                command += "\n"
            expanded = []
            norm_tok = token.decode("utf-8").lower()
            norm_tok = [i for i in unicodedata.normalize("NFKD",norm_tok) if not unicodedata.combining(i)]
            norm_tok = "".join(norm_tok).encode("utf-8")
            print >> sys.stderr, "TERMS:", norm_tok
            matches = word_pattern_search(norm_tok,db.locals["db_path"]+"/frequencies/normalized_word_frequencies")
            print >> sys.stderr, "MATCHES:"
            print >> sys.stderr, matches                
            for m in matches:
                if m not in expanded:
                    expanded += [m]                                              
            #subtokens should be expanded against word_frequencies here
            #AFTER unicode-stripping, of course.
            clauses[-1] += expanded
            command += "\n".join(subt for subt in expanded) + "\n"
#            print >> sys.stderr, expanded
        elif label == "NOT":
            #Need to decide something to do with NOT
            break
        prior_label = label
#        print clauses
#        print "\n".join("\n".join(c for c in clause) for clause in clauses) 
    print >> sys.stderr, command
    return command

def format_query(qstring,db):
    parsed = parse_query(qstring)
    parsed_split = []
    for label,token in parsed:
        l,t = label,token
        if l == "QUOTE":
            subtokens = t[1:-1].split(" ")
            parsed_split += [("QUOTE_S",sub_t) for sub_t in subtokens if sub_t]
        else:
            parsed_split += [(l,t)]
    command = format_parsed_query(parsed_split,db)
    return command

def word_pattern_search(term, path):
    command = ['egrep', '-wi', "^%s" % term, '%s' % path]
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    match, stderr = process.communicate()
    print >> sys.stderr, "RESULTS:",repr(match)
    match = match.split('\n')
    match.remove('')
    ## HACK: The extra decode/encode are there to fix errors when this list is converted to a json object
    return [m.split("\t")[1].strip().decode('utf-8', 'ignore').encode('utf-8') for m in match]

def old_format_query(qstring):
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
