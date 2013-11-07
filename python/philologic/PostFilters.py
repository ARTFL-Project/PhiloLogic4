#!/usr/bin/env python
import sys
import os
import sqlite3
import unicodedata
from collections import defaultdict


DefaultPostFilters = [word_frequencies,normalized_word_frequencies,metadata_frequencies,normalized_metadata_frequencies]


def word_frequencies(loader_obj):
    frequencies = loader_obj.destination + '/frequencies'
    os.system('mkdir %s' % frequencies)
    output = open(frequencies + "/word_frequencies", "w")
    for line in open(loader_obj.destination + '/WORK/all_frequencies'):
        count, word = tuple(line.split())
        print >> output, word + '\t' + count
    output.close()
    
def normalized_word_frequencies(loader_obj):
    frequencies = loader_obj.destination + '/frequencies'
    output = open(frequencies + "/normalized_word_frequencies", "w")
    for line in open(frequencies + '/word_frequencies'):
        word, count = line.split("\t")
        norm_word = word.decode('utf-8').lower()
        norm_word = [i for i in unicodedata.normalize("NFKD",norm_word) if not unicodedata.combining(i)]
        norm_word = ''.join(norm_word).encode('utf-8')
        print >> output, norm_word + "\t" + word
#        word_dict[word] += int(count)
#    for norm_word, norm_word_count in sorted(word_dict.items(), key=lambda x: x[1], reverse=True):
#        print >> output, norm_word + '\t' + str(norm_word_count)
    output.close()
    
def metadata_frequencies(loader_obj):
    frequencies = loader_obj.destination + '/frequencies'
    conn = sqlite3.connect(loader_obj.destination + '/toms.db')
    c = conn.cursor()
    for field in loader_obj.metadata_fields:
        query = 'select %s, count(*) from toms group by %s order by count(%s) desc' % (field, field, field)
        try:
            c.execute(query)
            output = open(frequencies + "/%s_frequencies" % field, "w")
            for result in c.fetchall():
                if result[0] != None:
                    val = result[0].encode('utf-8', 'ignore') 
                    clean_val = val.replace("\n"," ").replace("\t","")
                    print >> output, clean_val + '\t' + str(result[1])
            output.close()
        except sqlite3.OperationalError:
            print >> sys.stderr, "error writing " + field + "_frequencies"
    conn.close()
    
def normalized_metadata_frequencies(loader_obj):
    frequencies = loader_obj.destination + '/frequencies'
    for field in loader_obj.metadata_fields:
        print >> sys.stderr, "normalizing " + field
        try:
            output = open(frequencies + "/normalized_" + field + "_frequencies","w")        
            for line in open(frequencies + "/" + field + "_frequencies"):            
                word, count = line.split("\t")
                norm_word = word.decode('utf-8').lower()
                norm_word = [i for i in unicodedata.normalize("NFKD",norm_word) if not unicodedata.combining(i)]
                norm_word = ''.join(norm_word).encode('utf-8')
                print >> output, norm_word + "\t" + word
            output.close()
        except:
            print >> sys.stderr, "error writing normalized_" + field + "_frequencies"

# Some post-merge cleanup for normalize_divs in LoadFilters--should always be paired and use same arguments.
def normalize_divs_post(*columns):
    def normalize_these_columns_post(loader):
        for k,v in loader.metadata_types.items():
            if k in columns:
                loader.metadata_types[k] = "div3"
    return normalize_these_columns_post
