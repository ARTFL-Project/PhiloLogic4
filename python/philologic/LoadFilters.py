#!/usr/bin/env python

import os
import re
import cPickle
import unicodedata
from subprocess import Popen, PIPE
from philologic.OHCOVector import Record
from ast import literal_eval as eval
import sys


## Default filters
def normalize_unicode_raw_words(loader_obj, text):
    tmp_file = open(text["raw"] + ".tmp","w")
    for line in open(text["raw"]):
        rec_type, word, id, attrib = line.split('\t')
        id = id.split()
        if rec_type == "word":
            word = word.decode("utf-8").lower().encode("utf-8")
        record = Record(rec_type, word, id)
        record.attrib = eval(attrib)
        print >> tmp_file, record
    os.remove(text["raw"])
    os.rename(text["raw"] + ".tmp",text["raw"])
    
def make_word_counts(loader_obj, text, depth=5):
    object_types = ['doc', 'div1', 'div2', 'div3', 'para', 'sent', 'word']
    counts = [0 for i in range(depth)]
    temp_file = text['raw'] + '.tmp'
    output_file = open(temp_file, 'w')
    for line in open(text['raw']):
        type, word, id, attrib = line.split('\t')
        id = id.split()
        record = Record(type, word, id)
        record.attrib = eval(attrib)
        for d,count in enumerate(counts):
            if type == 'word':
                counts[d] += 1
            elif type == object_types[d]:
                record.attrib['word_count'] = counts[d]
                counts[d] = 0
        print >> output_file, record
    output_file.close()
    os.remove(text['raw'])
    os.rename(temp_file, text['raw'])

def generate_words_sorted(loader_obj, text):
    wordcommand = "cat %s | egrep \"^word\" | sort %s %s > %s" % (text["raw"],loader_obj.sort_by_word,loader_obj.sort_by_id,text["words"])
    os.system(wordcommand)

def make_object_ancestors(*types):
    ## We should add support for a 'div' type in the future
    type_depth = {'doc':1, 'div1': 2, 'div2': 3, 'div3': 4, 'para': 5,
                        'sent': 6, 'word': 7}
    
    def inner_make_object_ancestors(loader_obj, text):
        temp_file = text['words'] + '.tmp'
        output_file = open(temp_file, 'w')
        for line in open(text['words']):
            type, word, id, attrib = line.split('\t')
            id = id.split()
            record = Record(type, word, id)
            record.attrib = eval(attrib)
            for type in types:
                zeros_to_add = ['0' for i in range(7 - type_depth[type])]
                philo_id = id[:type_depth[type]] + zeros_to_add
                record.attrib[type + '_ancestor'] = ' '.join(philo_id)
            print >> output_file, record
        output_file.close()
        os.remove(text['words'])
        os.rename(temp_file, text['words'])
    return inner_make_object_ancestors

def make_sorted_toms(*types):
    def sorted_toms(loader_obj, text):
        type_pattern = "|".join("^%s" % t for t in types)
        tomscommand = "cat %s | egrep \"%s\" | sort %s > %s" % (text["raw"],type_pattern,loader_obj.sort_by_id,text["sortedtoms"])
        os.system(tomscommand)
    return sorted_toms

def prev_next_obj(*types):
    """Store the previous and next object for every object passed to this function
    By default, this is doc, div1, div2, div3."""
    types = list(types)
    def inner_prev_next_obj(loader_obj, text):
        record_dict = {}
        temp_file = text['raw'] + '.tmp'
        output_file = open(temp_file, 'w')
        for line in open(text['sortedtoms']):
            type, word, id, attrib = line.split('\t')
            id = id.split()
            record = Record(type, word, id)
            record.attrib = eval(attrib) 
            if type in record_dict:
                record_dict[type].attrib['next'] = ' '.join(id)
                if type in types:
                    print >> output_file, record_dict[type]
                else:
                    del record_dict[type].attrib['next']
                    del record_dict[type].attrib['prev']
                    print >> output_file, record_dict[type]
                record.attrib['prev'] = ' '.join(record_dict[type].id)
                record_dict[type] = record
            else:
                record.attrib['prev'] = ''
                record_dict[type] = record
        types.reverse()
        for obj in types:
            try:
                record_dict[obj].attrib['next'] = ''
                print >> output_file, record_dict[obj]
            except KeyError:
                pass
        output_file.close()
        os.remove(text['sortedtoms'])
        type_pattern = "|".join("^%s" % t for t in loader_obj.types)
        tomscommand = "cat %s | egrep \"%s\" | sort %s > %s" % (temp_file,type_pattern,loader_obj.sort_by_id,text["sortedtoms"])
        os.system(tomscommand)
        os.remove(temp_file)
    return inner_prev_next_obj     
    
def generate_pages(loader_obj, text):
    pagescommand = "cat %s | egrep \"^page\" > %s" % (text["raw"],text["pages"])
    os.system(pagescommand)
    
def make_max_id(loader_obj, text):
    max_id = [0,0,0,0,0,0,0,0,0]
    for line in open(text["words"]):
        (key,type,id,attr) = line.split("\t")
        id = [int(i) for i in id.split(" ")]
        max_id = [max(new,prev) for new,prev in zip(id,max_id)]
    rf = open(text["results"],"w")
    cPickle.dump(max_id,rf) # write the result out--really just the resulting omax vector, which the parent will merge in below.
    rf.close()
    


##Useful for nested metadata.  Should always pair with normalize_divs_post in postFilters
def normalize_divs(*columns):
    def normalize_these_columns(loader_obj,text):
        current_values = {}
        tmp_file = open(text["sortedtoms"] + ".tmp","w")
        for column in columns:
            current_values[column] = ""
        for line in open(text["sortedtoms"]):
            type, word, id, attrib = line.split('\t')
            id = id.split()
            record = Record(type, word, id)
            record.attrib = eval(attrib)
            if type == "div1":
                for column in columns:
                    if column in record.attrib:
                        current_values[column] = record.attrib[column]
                    else:
                        current_values[column] = ""
            elif type == "div2":
                for column in columns:
                    if column in record.attrib:
                        current_values[column] = record.attrib[column]
            elif type == "div3":
                for column in columns:
                    if column not in record.attrib:
                        record.attrib[column] = current_values[column]
            print >> tmp_file, record
        tmp_file.close()
        os.remove(text["sortedtoms"])
        os.rename(text["sortedtoms"] + ".tmp",text["sortedtoms"])
    return normalize_these_columns



def normalize_unicode_columns(*columns):
#I should never, ever need to use this now.
    def smash_these_unicode_columns(loader_obj, text):
        tmp_file = open(text["sortedtoms"] + ".tmp","w")
        for line in open(text["sortedtoms"]):
            type, word, id, attrib = line.split('\t')
            id = id.split()
            record = Record(type, word, id)
            record.attrib = eval(attrib)
            for column in columns:
                if column in record.attrib:
#                    print >> sys.stderr, repr(record.attrib)
                    col = record.attrib[column].decode("utf-8")
                    col = col.lower()
                    smashed_col = [c for c in unicodedata.normalize("NFKD",col) if not unicodedata.combining(c)]
                    record.attrib[column + "_norm"] = ''.join(smashed_col).encode("utf-8")
                    #record.attrib[column + "_norm"] = ''.join([c.encode("utf-8") for c in unicodedata.normalize('NFKD',record.attrib[column].decode("utf-8").lower()) if not unicodedata.combining(c)])
            print >> tmp_file, record
        tmp_file.close()
        os.remove(text["sortedtoms"])
        os.rename(text["sortedtoms"] + ".tmp",text["sortedtoms"])
    return smash_these_unicode_columns
    


### Optional filters
def tree_tagger(tt_path,param_file,maxlines=20000):
    def tag_words(loader_obj,text):  
        # Set up the treetagger process
        tt_args = [tt_path,"-token","-lemma","-prob",'-no-unknown', "-threshold",".01",param_file]
        ttout_fh = open(text["raw"]+".ttout","w")
        tt_worker = Popen(tt_args,stdin=PIPE,stdout=ttout_fh)
        raw_fh = open(text["raw"],"r")
        line_count = 0
    
        # read through the object file, pass the words to treetagger
        for line in raw_fh:
            type, word, id, attrib = line.split('\t')        
            id = id.split()
            if type == "word":
                word = word.decode('utf-8', 'ignore').lower().encode('utf-8')
                # close and re-open the treetagger process to prevent garbage output.
                if line_count > maxlines:
                    tt_worker.stdin.close()
                    tt_worker.wait()
                    new_ttout_fh = open(text["raw"]+".ttout","a")
                    tt_worker = Popen(tt_args, stdin=PIPE,stdout=new_ttout_fh)
                    line_count = 0
                print >> tt_worker.stdin, word
                line_count += 1
    
        # finish tagging        
        tt_worker.stdin.close()
        tt_worker.wait()
    
        # go back through the object file, and add the treetagger results to each word
        tmp_fh = open(text["raw"]+".tmp","w")
        tag_fh = open(text["raw"] + ".ttout","r")    
        for line in open(text["raw"],"r"):
            type, word, id, attrib = line.split('\t')
            id = id.split()
            record = Record(type,word,id)
            record.attrib = eval(attrib)                
            if type == "word":
                tag_l = tag_fh.readline()
                next_word,tag = tag_l.split("\t")[0:2]
                pos,lem,prob = tag.split(" ")
                if next_word != word.decode('utf-8', 'ignore').lower().encode('utf-8'):
                    print >> sys.stderr, "TREETAGGER ERROR:",next_word," != ",word,pos,lem
                    return
                else:
                    record.attrib["pos"] = pos
                    record.attrib["lemma"] = lem
                    print >> tmp_fh, record
            else:
                print >> tmp_fh, record
        os.remove(text["raw"])
        os.rename(text["raw"] + ".tmp",text["raw"])
        os.remove(text["raw"] + ".ttout")
    return tag_words

def evaluate_word(word, word_pattern):
    word = word.decode('utf-8', 'ignore')
    if word_pattern.search(word) and len(word) > 1:
        return True
    else:
        return False

def store_in_plain_text(*types):
    object_types = {'doc': 1, 'div1': 2, 'div2': 3, 'div3': 4, 'para': 5,
                    'sent': 6, 'word': 7}
    obj_to_track = []
    for obj in types:
        if obj not in object_types:
            print >> sys.stderr, "%s object type not supported",
            print >> sys.stderr, "only 'doc', 'div1', 'div2' and 'div3' are supported"
        obj_to_track.append(object_types[obj])
    
    def inner_store_in_plain_text(loader_obj, text):
        files_path = loader_obj.destination + '/plain_text_objects/'
        word_pattern = re.compile('[^\W\d_]', re.UNICODE)
        try:
            os.mkdir(files_path)
        except OSError:
            ## Path was already created                                                                                                                                       
            pass
        for obj_depth in obj_to_track:
            old_philo_id = []
            philo_id = []
            words = []
            for line in open(text['raw']):
                type, word, id, attrib = line.split('\t')
                if type != 'word':
                    continue
                ## Check if we're in the top level object
                if evaluate_word(word, word_pattern):
                    philo_id = id.split()[:obj_depth]
                    if not old_philo_id:
                        old_philo_id = philo_id
                    if philo_id != old_philo_id: 
                        filename = files_path + '_'.join(old_philo_id)
                        output = open(filename, 'w')
                        print >> output, ' '.join(words)
                        output.close()
                        words = []
                        old_philo_id = philo_id
                    words.append(word)
            if words:
                filename = files_path + '_'.join(philo_id)
                output = open(filename, 'w')
                print >> output, ' '.join(words)
                output.close()
                
    return inner_store_in_plain_text



## If you are going to change the order of these filters (which is not recommended)
## please consult the documentation for each of these filters in LoadFilters.py
DefaultLoadFilters = [normalize_unicode_raw_words, make_word_counts,generate_words_sorted,
                      make_object_ancestors('doc', 'div1', 'div2', 'div3'), make_sorted_toms("doc","div1","div2","div3"),
                      prev_next_obj('doc', 'div1', 'div2', 'div3'), generate_pages, make_max_id]
