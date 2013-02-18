#!/usr/bin/env python

import re
import sys
import os
import subprocess


accents = {'A': "(a|\xc3\xa0|\xc3\xa1|\xc3\xa2|\xc3\xa3|\xc3\xa4|\xc3\x82)",
           'C': "(c|\xc3\xa7|\xc3\x87)",
           'E': "(e|\xc3\xa8|\xc3\xa9|\xc3\xaa|\xc3\xab|\xc3\x89|\xc3\x88|\xc3\x8A)",
           'I': "(i|\xc3\xac|\xc3\xad|\xc3\xae|\xc3\xaf)",
           'N': "(n|\xc3\xb1)",
           'O': "(o|\xc3\xb2|\xc3\xb3|\xc3\xb4|\xc3\xb4|\xc3\xb6|\xc3\x94)",
           'U': "(u|\xc3\xb9|\xc3\xba|\xc3\xbb|\xc3\xbc)",  
           'Y': "(y|\xc3\xbf|xc3\xbd)"}

word_char = re.compile('([A-Z]+|\*)')

def expand_query(term, path):
    ## Look for uppercase letters and replace with regex pattern
    for uppercase in accents:
        if term.find(uppercase) != -1:
            term = term.replace(uppercase, accents[uppercase])
    
    ## Add wildcard and search for pattern
    term = term.replace('*', '.*')
    matching_list = word_pattern_search(term, path)
    matching_list = [i.strip() for i in matching_list if i]
    return matching_list
    
def word_pattern_search(term, path):
    if re.search('\*', term):
        term = term.replace('*', '.*')
        command = ['egrep', '-ie', "^%s" % term, '%s' % path]
    else:
        command = ['egrep', '-ie', "^%s\s" % term, '%s' % path]
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    match, stderr = process.communicate()
    match = match.split('\n')
    match.remove('')
    ## HACK: The extra decode/encode are there to fix errors when this list is converted to a json object
    return [m.split()[0].strip().decode('utf-8', 'ignore').encode('utf-8') for m in match]
    
def metadata_pattern_search(term, path):
    term = '(.* |^)%s.*' % term
    command = ['egrep', '-oie', "%s\W" % term, '%s' % path]
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    match, stderr = process.communicate()
    return [m.strip() for m in match.split('\n')]

def word_exploder(terms):
    """ Expand queries"""
    ## Get path to the word_frequencies file
    path = os.environ['SCRIPT_FILENAME']
    path = path.replace('dispatcher.py', '')
    path += 'data/frequencies/word_frequencies'
    
    ## Iterate through query
    matching_list = ''
    for t in terms.split():
        if word_char.search(t):
            t = '|'.join(expand_query(t, path))
        matching_list = matching_list + ' ' + t
        
    matching_list = matching_list.strip()
    return matching_list

def query_parser(query):
    query = query.strip()
    query = query.replace('  ', ' ')
    if word_char.search(query):
        query = word_exploder(query)
    return query
