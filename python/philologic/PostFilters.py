#!/usr/bin/env python
import sys
import os
import sqlite3
import unicodedata
import gzip
from collections import defaultdict



def make_sql_table(table, file_in, db_file="toms.db", gz=False, indices=[], depth=7):
    def inner_make_sql_table(loader_obj):
        print "Loading the %s SQLite table..." % table,
        db_destination = os.path.join(loader_obj.destination, db_file)
        conn = sqlite3.connect(db_destination)
        conn.text_factory = str
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        columns = 'philo_type,philo_name,philo_id,philo_seq'
        query = 'create table if not exists %s (%s)' % (table, columns)
        c.execute(query)
        
        sequence = 0
        if gz:
            file_in_handle = gzip.open(file_in, "rb")
        else:
            file_in_handle = open(file_in)
        for line in file_in_handle:
            philo_type, philo_name, id, attrib = line.split("\t",3)
            fields = id.split(" ",8)
            if len(fields) == 9:
                row = {}
                philo_id = " ".join(fields[:depth])
                row["philo_type"] = philo_type
                row["philo_name"] = philo_name
                row["philo_id"] = philo_id
                row["philo_seq"] = sequence
                row.update(eval(attrib))
                columns = "(%s)" % ",".join([i for i in row])
                insert = "INSERT INTO %s %s values (%s);" % (table, columns,",".join(["?" for i in row]))
                values = [v for k,v in row.items()]
                try:
                    c.execute(insert,values)
                except sqlite3.OperationalError:
                    c.execute("PRAGMA table_info(%s)" % table)
                    column_list = [i[1] for i in c.fetchall()]
                    for column in row:
                        if column not in column_list:
                            c.execute("ALTER TABLE %s ADD COLUMN %s;" % (table,column))
                    c.execute(insert,values)
                sequence += 1       
        conn.commit()
        
        for index in indices:
            try:
                if isinstance(index, str):
                    index = (index,) 
                index_name = '%s_%s_index' % (table,'_'.join(index))
                index = ','.join(index)
                c.execute('create index if not exists %s on %s (%s)' % (index_name,table,index))
            except sqlite3.OperationalError:
                pass
        conn.commit()
        conn.close()
        
        if not loader_obj.debug:
            os.system('rm %s' % file_in)
    return inner_make_sql_table

def word_frequencies(loader_obj):
    print 'Generating word frequencies...',
    frequencies = loader_obj.destination + '/frequencies'
    os.system('mkdir %s' % frequencies)
    output = open(frequencies + "/word_frequencies", "w")
    for line in open(loader_obj.destination + '/WORK/all_frequencies'):
        count, word = tuple(line.split())
        print >> output, word + '\t' + count
    output.close()
    
def normalized_word_frequencies(loader_obj):
    print 'Generating normalized word frequencies...',
    frequencies = loader_obj.destination + '/frequencies'
    output = open(frequencies + "/normalized_word_frequencies", "w")
    for line in open(frequencies + '/word_frequencies'):
        word, count = line.split("\t")
        norm_word = word.decode('utf-8').lower()
        norm_word = [i for i in unicodedata.normalize("NFKD",norm_word) if not unicodedata.combining(i)]
        norm_word = ''.join(norm_word).encode('utf-8')
        print >> output, norm_word + "\t" + word
    output.close()
    
def metadata_frequencies(loader_obj):
    print 'Generating metadata frequencies...'
    frequencies = loader_obj.destination + '/frequencies'
    conn = sqlite3.connect(loader_obj.destination + '/toms.db')
    c = conn.cursor()
    fields_not_found = []
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
            print >> sys.stderr, 'Generated metadata frequencies for %s' % field
        except sqlite3.OperationalError:
            fields_not_found.append(field)
    if fields_not_found:
        print >> sys.stderr, 'The following fields were not found in the input corpus %s' % ', '.join(fields_not_found)
    conn.close()
    
def normalized_metadata_frequencies(loader_obj):
    print 'Generating normalized metadata frequencies...',
    frequencies = loader_obj.destination + '/frequencies'
    for field in loader_obj.metadata_fields:
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
            pass

# Some post-merge cleanup for normalize_divs in LoadFilters--should always be paired and use same arguments.
def normalize_divs_post(*columns):
    def normalize_these_columns_post(loader):
        for k,v in loader.metadata_types.items():
            if k in columns:
                loader.metadata_types[k] = "div3"
    return normalize_these_columns_post


DefaultPostFilters = [word_frequencies,normalized_word_frequencies,metadata_frequencies,normalized_metadata_frequencies]
