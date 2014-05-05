#!/usr/bin/env python

import os
import sys
import sqlite3
from philologic.DB import DB

def biblio_criteria(q, config, time_series=False):
    """Generates clickable bibligraphic criteria in search results"""
    biblio = []
    if time_series:
        del q["metadata"]["date"]
    for k,v in q["metadata"].iteritems():
        if v:
            close_icon = '<span class="ui-icon ui-icon-circle-close remove_metadata" data-metadata="%s"></span>' % k
            if k in config.metadata_aliases:
                k = config.metadata_aliases[k]
            biblio.append('<span class="biblio_criteria">%s: <b>%s</b> %s</span>' % (k.title(), v.decode('utf-8', 'ignore'), close_icon))
    return ' '.join(biblio)

def search_examples(field):
    path = os.getcwd().replace('functions', "").replace('scripts', '').replace('reports', '') + '/data/'
    db = DB(path,encoding='utf-8')
    if field == "word":
        word_path = path + '/frequencies/word_frequencies'
        word = ''
        for n,line in enumerate(open(word_path)):
            word = line.split()[0]
            if n == 100:
                break
        return word.decode('utf-8', 'ignore')
    else:
        c = db.dbh.cursor()
        object_type = db.locals['metadata_types'][field]
        print >> sys.stderr, "FIELD", field
        try:
            if object_type != 'div':
                c.execute('select %s from toms where philo_type="%s" and %s!="" limit 1' % (field, object_type, field))
            else:
                c.execute('select %s from toms where philo_type="div1" or philo_type="div2" or philo_type="div3" and %s!="" limit 1' % (field, field))
        except sqlite3.OperationalError:
            example = ''
        try:
            example = c.fetchone()[0].decode('utf-8', 'ignore')
        except (TypeError, AttributeError):
            example = ''
        return example