#!/usr/bin/env python
import urllib
from wsgiref.util import shift_path_info
import urlparse
import re
import sys
import os
from philologic.DB import DB
from link import *

def make_abs_doc_cite_mobile(db, i):
    """ Returns a representation of a PhiloLogic object suitable for a bibliographic report. """
    author = i.doc.author or ''
    if author:
        author = "%s, " % author
    record = u"%s<i><a data-id='%s' class='biblio_cite'>%s</a></i>" % (i.doc.author, ' '.join([str(j) for j in i.philo_id]),i.doc.title)
    date = i.doc.date
    if date:
        record += " [%s]" % date
    return record

def make_abs_doc_shrtcit_mobile(db, i):
    """ Returns a representation of a PhiloLogic object suitable for a (short) bibliographic report. """
    author = i.doc.author or ''
    if author:
        cmc_author = author.split(",", 1)[0] + ", "
    else:
        cmc_author = author
    section_names = [i.div1.head,i.div2.head,i.div3.head]
    head = section_names[2] or section_names[1] or section_names[0]
    record = cmc_author + i.doc.title + ": " + head
    return record
    
def make_abs_doc_cite_biblio_mobile(db, i):
    """ Returns a representation of a PhiloLogic object suitable for a bibliographic report. """
    record = u"%s|<i><span class='biblio_cite'>%s</span></i>" % (i.doc.author,i.doc.title)
    #date = i.doc.date
    #if date:
    #    record += " [<b>%s</b>] " % date
    more_metadata = []
    pub_place = i.doc.pub_place
    if pub_place:
        more_metadata.append(pub_place)
    collection = i.doc.collection
    if collection:
        more_metadata.append(collection)
    publisher = i.doc.publisher
    if publisher:
        more_metadata.append(publisher)
    date = i.doc.date
    if date:
        try:
            date = str(date)
            more_metadata.append(date)
        except:
            pass
    if more_metadata:
        record += '(%s)' % ' '.join(more_metadata)
    genre = i.doc.text_genre
    if genre:
        record += ' [genre: %s]' % genre
    return record
