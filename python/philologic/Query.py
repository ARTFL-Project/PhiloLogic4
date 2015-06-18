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
    dir = db.path + "/hitlists/"
    filename = filename or (dir + hfile)
    hl = open(filename, "w")
    err = open("/dev/null", "w")
    freq_file = db.path+"/frequencies/normalized_word_frequencies"
    if (query_debug):
        print >> sys.stderr, "FORKING"
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
            if query_debug:
                print >> sys.stderr, "WORKER DETACHED at ", datetime.now() - tstart
#            args = ["search4", db.path,"--limit",str(limit)]
            args = ["corpus_search"]
            if corpus_file:
                args.extend(("-c", corpus_file));
#            if corpus_file and corpus_size:
#                args.extend(("--corpusfile", corpus_file , "--corpussize" , str(corpus_size)))
            if method and method_arg:
                args.extend(("-m",method,"-a",str(method_arg)))
            
            args.extend(("-o","binary",db.path,));

            worker = subprocess.Popen(args,stdin=subprocess.PIPE,stdout=hl,stderr=err)
            # if query_debug:
            #     print >> sys.stderr, "WORKER STARTED:"," ".join(args);

            query_log_fh = filename + ".terms"
            print >> sys.stderr, "LOGGING TERMS to " + filename + ".terms"
            logger = subprocess.Popen(["tee",query_log_fh],stdin=subprocess.PIPE,stdout = worker.stdin)
            # print >> sys.stderr, "EXPANDING"
            expand_query_not(split,freq_file,logger.stdin)
            logger.stdin.close()


            # if query_debug == True:
            #     print >> sys.stderr, "DEBUGGING"
            #     query_log_fh = filename + ".terms"
            #     print >> sys.stderr, "LOGGING to " + filename + ".terms"
            #     logger = subprocess.Popen(["tee",query_log_fh],stdin=subprocess.PIPE,stdout = worker.stdin)
            #     print >> sys.stderr, "EXPANDING"
            #     expand_query_not(split,freq_file,logger.stdin)
            #     logger.stdin.close()
            # else:
            #     expand_query_not(split,freq_file,worker.stdin)

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

def get_expanded_query(hitlist):
	fn = hitlist.filename + ".terms"
	query = []
	term = []
	try:
		grep_results = open(fn,"r")
	except:
		return []
	for line in grep_results:
		if line == "\n":
			query.append(term)
			term = []
		else:
			term.append('"' + line[:-1] + '"')
	if term:
		query.append(term)		
	return query

def split_terms(grouped):
    #print >> sys.stderr, repr(grouped)
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
    #print >> sys.stderr, repr(split)
    return split

def expand_query(split, freq_file, dest_fh):
    first = True
    grep_proc = None
    #print >> sys.stderr, "EXPANDING", repr(split)
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


def expand_query_not(split, freq_file, dest_fh):
    first = True
    grep_proc = None
    #print >> sys.stderr, "SPLIT", repr(split)
    for group in split:
        if first == True:
            first = False
        else: # bare newline starts a new group, except the first
            dest_fh.write("\n")

        #find all the NOT terms and separate them out by type
        exclude= []
        term_exclude = []
        quote_exclude = []

        #print >> sys.stderr, "GROUP", repr(group)
        for i, g in enumerate(group):
            #print >> sys.stderr, i,"G", repr(g)
            kind, token = g
            if kind == "NOT":
                exclude = group[i+1:]
                group = group[:i]

                for kind, token in exclude:
                    if kind == "TERM":
                        term_exclude.append((kind,token))
                    if kind == "QUOTE":
                        quote_exclude.append((kind,token))
                break

        #print >> sys.stderr, "OUTPUT", repr(dest_fh)

        # set up the basic filter to get the terms sorted and ready for the search engine
        if len(group) > 1:
            cut_proc = subprocess.Popen("cut -f 2", stdin=subprocess.PIPE,stdout=dest_fh, shell=True)  
        else:
            cut_proc = subprocess.Popen("cut -f 2 | sort | uniq", stdin=subprocess.PIPE,stdout=dest_fh, shell=True)
        filter_inputs = [cut_proc.stdin]
        filter_procs = [cut_proc]

        # We will chain all NOT operators backward from the main filter.
        for kind, token in exclude:
            if kind == "TERM":
                proc = invert_grep(token,subprocess.PIPE,filter_inputs[0])
            if kind == "QUOTE":
                proc = invert_grep_exact(token,subprocess.PIPE,filter_inputs[0])    
            filter_inputs = [proc.stdin] + filter_inputs  
            filter_procs = [proc] + filter_procs

        # then we append output from all the greps into the front of that filter chain.
        for kind,token in group: # or, splits, and ranges should have been taken care of by now.
            if kind == "TERM" or kind == "RANGE":
                grep_proc = grep_word(token,freq_file,filter_inputs[0])
                grep_proc.wait()
            elif kind == "QUOTE":
#                filter_inputs[0].write(token[1:-1] + "\t" + token[1:-1] + "\n") 
                grep_proc = grep_exact(token,freq_file,filter_inputs[0])
                grep_proc.wait()
        # close all the pipes and wait for procs to finish.
        for pipe,proc in zip(filter_inputs,filter_procs):
            pipe.close()
            proc.wait()

def grep_word(token,freq_file,dest_fh):
    #print >> sys.stderr, "GREP_WORD_TOKEN", repr(token)
#    norm_tok_uni = token.decode("utf-8").lower()
    norm_tok_uni = token.decode("utf-8")
    norm_tok_uni_chars = [i for i in unicodedata.normalize("NFKD",norm_tok_uni) if not unicodedata.combining(i)]
    norm_tok = u"".join(norm_tok_uni_chars).encode("utf-8")
    grep_command = ['egrep', '^%s[[:blank:]]' % norm_tok, '%s' % freq_file]
    grep_proc = subprocess.Popen(grep_command,stdout=dest_fh)
    return grep_proc

def invert_grep(token, in_fh, dest_fh):
    norm_tok_uni = token.decode("utf-8")
    norm_tok_uni_chars = [i for i in unicodedata.normalize("NFKD",norm_tok_uni) if not unicodedata.combining(i)]
    norm_tok = u"".join(norm_tok_uni_chars).encode("utf-8")
    grep_command = ['egrep', '-v', '^%s[[:blank:]]' % norm_tok]
    grep_proc = subprocess.Popen(grep_command,stdin=in_fh,stdout=dest_fh)
    return grep_proc

def grep_exact(token, in_fh, dest_fh):
    grep_command = ["egrep", "[[:blank:]]%s$" % token[1:-1]]
    print >> sys.stderr, grep_command
    grep_proc = subprocess.Popen(grep_command,stdin=in_fh,stdout=dest_fh)
    return grep_proc

def invert_grep_exact(token, in_fh, dest_fh):
    #don't strip accent or case, exact match only.
    grep_command = ["egrep", "-v", "[[:blank:]]%s$" % token[1:-1]]
    print >> sys.stderr, grep_command
    grep_proc = subprocess.Popen(grep_command,stdin=in_fh,stdout=dest_fh)
    #can't wait because input isn't ready yet.
    return grep_proc

if __name__ == "__main__":
    path = sys.argv[1]
    terms = sys.argv[2:]
    parsed = parse_query(" ".join(terms))
    print >> sys.stderr, "PARSED:", parsed
    grouped = group_terms(parsed)
    print >> sys.stderr, "GROUPED:", grouped
    split = split_terms(grouped)
    print >> sys.stderr, "parsed %d terms:" % len(split), split

    class Fake_DB: pass

    fake_db = Fake_DB()
    fake_db.locals = {"db_path":path + "/data/"}
    fake_db.path = path + "/data/"
    fake_db.encoding = "utf-8"
    freq_file = path + "/data/frequencies/normalized_word_frequencies"    
#    freq_file = "/Library/WebServer/Documents/philologic/plain_text_test/data/frequencies/normalized_word_frequencies"
    expand_query_not(split,freq_file,sys.stdout)
    hits = query(fake_db," ".join(terms),query_debug = True)
