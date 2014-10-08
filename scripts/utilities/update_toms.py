#!/usr/bin/env python

import sqlite3
import sys
import re
from philologic.PostFilters import metadata_frequencies, normalized_metadata_frequencies


def change_metadata(metadata_field):
    updated_metadata = re.sub('.*(\d{4}).*', '\\1', metadata_field)
    return updated_metadata

def update_function(c, field, db_location):
    query = 'select philo_id, %s from toms where philo_type="doc"' % field
    c.execute(query)
    updated_value = {}
    for i in c.fetchall():
        philo_id, metadata_field = i
        updated_value[philo_id] = change_metadata(metadata_field)
    
    ## Update SQL table
    for id, new_value in updated_value.iteritems():
        update_query = 'update toms set %s="%s" where philo_id="%s"' % (field, new_value, id)
        c.execute(update_query)
    conn.commit()
    conn.close()
        
    ## Update frequency file
    loader_obj = LoaderObj(db_location, field)
    print loader_obj.destination, loader_obj.metadata_fields
    metadata_frequencies(loader_obj)
    normalized_metadata_frequencies(loader_obj)

def parse_command_line(args):
    if len(args) == 1 or len(args) == 2:
        print "You need two arguments to execute this script"
        print "python update_toms.py db_location field_to_update"
        sys.exit()
    db_location = sys.argv[1]
    field = sys.argv[2]
    return db_location, field

def connect_to_db(db_location):
    conn = sqlite3.connect(db_location + '/data/toms.db')
    cursor = conn.cursor()
    return conn, cursor


## Build a loader class with the attributes needed to update the frequency files
class LoaderObj(object):
    
    def __init__(self, db_location, field):
        self.destination = db_location + '/data'
        self.metadata_fields = [field]


if __name__ == '__main__':
    db_location, field = parse_command_line(sys.argv)
    conn, c = connect_to_db(db_location)
    update_function(c, field, db_location)
    
    



