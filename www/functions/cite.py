#!/usr/bin/env python
import urllib
from wsgiref.util import shift_path_info
import urlparse
import re
import sys
import os
from philologic.DB import DB
from link import *

def concordance_citation(db, config, i):
    """ Returns a representation of a PhiloLogic object and all its ancestors
        suitable for a precise concordance citation. """
    doc_href = make_absolute_object_link(config,i.philo_id[:1],i.bytes)
    section_href = make_absolute_object_link(config,i.philo_id[:2], i.bytes)
    sub_section_href = make_absolute_object_link(config,i.philo_id[:3], i.bytes)
    section_names = [i.div1.head,i.div2.head,i.div3.head]
    section_name = section_names[0]
    try:
        sub_section_name = section_names[1]
    except IndexError:
        sub_section_name = section_name
    title = '<a href="%s">%s</a>' % (doc_href, i.doc.title.strip())
    citation = "%s <i>%s</i>" % (i.doc.author.strip(),title)
    date = i.doc.date
    if date:
        citation += " [%s]" % str(date)
    if section_name:
        citation += u"<a href='%s'>%s</a>" % (section_href,section_name.strip())
    if sub_section_name:
        citation += u"<a href='%s'>%s</a>" % (sub_section_href,sub_section_name.strip())
    speaker_name = i.para.who
    if speaker_name:
        speaker_href = make_absolute_object_link(config, i.philo_id[:5], i.bytes)
        citation += "<a href='%s'>%s</a>" % (speaker_href, speaker_name)
    
    page_obj = i.get_page()
    if page_obj:
        if page_obj['n']:
            page_n = page_obj['n'].decode('utf-8', 'ignore')
            citation += u" [page %s] " % page_n    
    citation = u'<span class="philologic_cite">' + citation + "</span>" + repr(i.philo_id)
    return citation

def biblio_citation(db, config, i):
    """ Returns a representation of a PhiloLogic object suitable for a bibliographic report. """
    doc_href = make_absolute_object_link(config,i.philo_id[:1], i.bytes)
    #record = u"%s, <i><a href='%s'>%s</a></i>" % (i.doc.author, doc_href,i.doc.title)
    record = u"William Shakespeare, <i><a href='%s'>%s</a></i>" % (doc_href,i.doc.title)
    date = i.doc.date
    if date:
        record += " [%s]" % date
    if db.locals['debug'] == True:
        record += " %s" % i.doc.filename
    return record

def make_abs_doc_cite_mobile(db, i):
    """ Returns a representation of a PhiloLogic object suitable for a bibliographic report. """
    record = u"%s, <i><a data-id='%s' class='biblio_cite'>%s</a></i>" % (i.doc.author, ' '.join([str(j) for j in i.philo_id]),i.doc.title)
    date = i.doc.date
    if date:
        record += " [%s]" % date
    return record
