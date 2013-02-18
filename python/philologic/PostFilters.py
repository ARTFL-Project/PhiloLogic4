#!/usr/bin/env python

import os
import sqlite3
    
def word_frequencies(loader_obj):
    frequencies = loader_obj.destination + '/frequencies'
    os.system('mkdir %s' % frequencies)
    output = open(frequencies + "/word_frequencies", "w")
    for line in open(loader_obj.destination + '/WORK/all_frequencies'):
        count, word = tuple(line.split())
        print >> output, word + '\t' + count
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
