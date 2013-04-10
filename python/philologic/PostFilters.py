#!/usr/bin/env python

import os
import sqlite3
import unicodedata
from collections import defaultdict
    
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
    word_dict = defaultdict(int)
    for line in open(frequencies + '/word_frequencies'):
        word, count = tuple(line.split())
        word = word.decode('utf-8').lower()
        word = [i for i in unicodedata.normalize("NFKD",word) if not unicodedata.combining(i)]
        word = ''.join(word).encode('utf-8')
        word_dict[word] += int(count)
    for norm_word, norm_word_count in sorted(word_dict.items(), key=lambda x: x[1], reverse=True):
        print >> output, norm_word + '\t' + str(norm_word_count)
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
                    print >> output, result[0].encode('utf-8', 'ignore') + '\t' + str(result[1])
            output.close()
        except sqlite3.OperationalError:
            pass
    conn.close()

def metadata_relevance_table(loader_obj):
    if loader_obj.r_r_obj and len(loader_obj.r_r_obj) < 2: ## disable with more than 1 object, probably should use toms table then.
        for obj in loader_obj.r_r_obj:
            conn = sqlite3.connect(loader_obj.destination + '/toms.db')
            c = conn.cursor()
            c.execute('create table metadata_relevance as select * from toms where philo_type=?', (obj,))
            conn.commit()
            for metadata in loader_obj.metadata_fields:
                try:
                    c.execute('create index %s_metadata_relevance on metadata_relevance(%s)' % (metadata, metadata))
                except sqlite3.OperationalError: # column doesn't exist for some reason
                    pass
            conn.commit()
            conn.close()
