#!/usr/bin/env python
from subprocess import Popen, PIPE
import sys
import time
import hashlib
import os

args = sys.argv[1:]
dbname = sys.argv[1]
method = sys.argv[2]
arg = sys.argv[3]

old_method_aliases = {"prox":"proxy","sent":"cooc"}

NULL = open(os.devnull,"w")
search_input = ["demeura long", "demeura", "demure", "allons", "nous allons", "allons nous","nous|allons allons|nous","nous|vous allons", "nous|vous", "vous|nous", "un de ces"]
sys.stdin.close()

print >> sys.stderr, "./corpus_search", "-m", method, "-a", arg,dbname
print >> sys.stderr, "/bin/search4", "--ascii", "--limit","10000000",dbname, method, arg

for search_i in search_input:
    print >> sys.stderr, "querying for \"%s\"" % search_i
    search_input_terms = search_i.split(" ")
    search_input_tokens = [s.split("|") for s in search_input_terms]
    search_input_words = "\n\n".join("\n".join(t) for t in search_input_tokens) + "\n"
    search_input = search_input_words
    print >> sys.stderr, search_input

    search_method = method
    if method in old_method_aliases:
        search_method = old_method_aliases[method]
    search_proc = Popen(["/bin/search4", "--ascii", "--limit","10000000",dbname, search_method, arg],stdin=PIPE,stdout=PIPE,stderr=NULL)
    search_proc.stdin.write(search_input)
    search_proc.stdin.close()


    corpus_proc = Popen(["./corpus_search", "-m", method, "-a", arg,dbname],stdin=PIPE,stdout=PIPE,stderr=NULL)
    corpus_proc.stdin.write(search_input)
    corpus_proc.stdin.close()
    c = 0
    match = True

    c = 0

    for line in corpus_proc.stdout.readlines():

        hits = line[:-1].split(" :: ")
        fixed_line = []
        i = 0
        prefix = []
        words_bytes = []
        for hit in hits:
            n = hit.split(" ")
            if i == 0:
                prefix += n[:6] + [n[8]]
            words_bytes.append( [n[6],n[7]] )
            i += 1
        words_bytes.sort(key=lambda x:int(x[0]))
        fixed_line = prefix
        for w in words_bytes:
            fixed_line += w
        fixed_line = " ".join(fixed_line)
        c += 1

        if (match == False):
            pass
        else:
            comp_line = search_proc.stdout.readline()
            fixed_comp_line = []
            comp = comp_line[:-1].split(" ")
            fixed_comp_line = comp[:7]
            words_bytes = []
            i = 7
            while i < len(comp):
                words_bytes.append([comp[i],comp[i+1]])
                i += 2
            words_bytes.sort(key=lambda x:int(x[0]))
            for w in words_bytes:
                fixed_comp_line += w
            fixed_comp_line = " ".join(fixed_comp_line)
            if (fixed_comp_line != fixed_line):
                print >> sys.stderr, "\tfirst mismatch at hit %d; \n%s\n%s\n"% (c,fixed_line,fixed_comp_line)
                match = False
                other_c = c

    if match == True:
        other_c = c
    else:
        while search_proc.stdout.readline():
            other_c += 1

    print >> sys.stderr, "done.  %d/%d results" % (c,other_c)
