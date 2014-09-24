#!/usr/bin/env python

import sqlite3
from ast import literal_eval as eval

            
def word_counts_table(loader_obj, obj_type='doc'):
    object_types = ['doc', 'div1', 'div2', 'div3', 'para', 'sent', 'word']
    depth = object_types.index(obj_type) + 1 ## this is for philo_id slices
    
    ## Retrieve column names from toms.db
    original_fields = ['philo_type', 'philo_name', 'philo_id', 'philo_seq', '%s_token_count' % obj_type]
    toms_conn = sqlite3.connect(loader_obj.destination + '/toms.db')
    toms_conn.row_factory = sqlite3.Row
    toms_c = toms_conn.cursor()
    toms_c.execute('select * from toms')
    extra_fields = [i[0] for i in toms_c.description if i[0] not in original_fields]
    field_list = original_fields + extra_fields + ['bytes']
    
    ## Create table
    conn = sqlite3.connect(loader_obj.destination + '/%s_word_counts.db' % obj_type)
    conn.text_factory = str
    c = conn.cursor()
    columns = ','.join(field_list)
    query = 'create table if not exists toms (%s)' % columns
    c.execute(query)
    c.execute('create index word_index on toms (philo_name)')
    c.execute('create index philo_id_index on toms (philo_id)')
    conn.commit()
    
    file_in = '%s/%s_word_counts_sorted' % (loader_obj.workdir, obj_type)
    sequence = 0
    for line in open(file_in):
        (philo_type,philo_name,id,attrib) = line.split("\t",3)
        philo_id = ' '.join(id.split()[:depth])
        philo_id = philo_id + ' ' + ' '.join('0' for i in range(7 - depth))
        row = {}
        row["philo_type"] = philo_type
        row["philo_name"] = philo_name
        row["philo_id"] = philo_id
        row["philo_seq"] = sequence
        attrib = eval(attrib)
        
        ## Fetch missing fields from toms.db
        toms_query = 'select %s from toms where philo_id=?' % ','.join(extra_fields)
        toms_c.execute(toms_query, (philo_id,))
        results = [i for i in toms_c.fetchone()]
        row.update(dict(zip(extra_fields, results)))
        
        for k in attrib:
            row[k] = attrib[k]
        row_key = []
        row_value = []
        for k,v in row.items():
            row_key.append(k)
            row_value.append(v)
        key_string = "(%s)" % ",".join(x for x in row_key)
        insert = "INSERT INTO toms %s values (%s);" % (key_string,",".join("?" for i in row_value))
        c.execute(insert,row_value)
        sequence += 1       
    conn.commit()