#!/usr/bin/env python
import urllib
from wsgiref.util import shift_path_info
import urlparse
import re
import sys
import os
from philologic.DB import DB
from link import *

def make_abs_div_cite(db,i):
    """ Returns a representation of a PhiloLogic object and all it's ancestors suitable for a precise concordance citation. """
    doc_href = make_absolute_object_link(db,i.philo_id[:1],i.bytes)
    section_href = make_absolute_object_link(db,i.philo_id[:2], i.bytes)
    sub_section_href = make_absolute_object_link(db,i.philo_id[:3], i.bytes)
#    para_href = make_object_link(i.philo_id[:5], i.bytes)                                                                                                                                                                                                                         
    section_names = [i.div1.head,i.div2.head,i.div3.head]
    section_name = section_names[0]
    try:
        sub_section_name = section_names[1]
    except IndexError:
        sub_section_name = section_name
#    speaker_name = i.who                                                                                                                                                                                                                                                                                                                                                                                              
    title = '<a href="%s">%s</a>' % (doc_href, i.title)
    cite = u"<span class='philologic_cite'>%s <i>%s</i>" % (i.author,title)
    separation = '<span class="cite_separation"></span>'
    if section_name:
        cite += u"%s<a href='%s' class='section_name'>%s</a>" % (separation,section_href,section_name)
    if sub_section_name:
        cite += u"%s<a href='%s' class='sub_section_name'>%s</a>" % (separation,sub_section_href,sub_section_name)
    
    if db.locals['debug'] == True:
        cite += " %s" % i.filename
    page_obj = i.get_page()
    if page_obj:
            if page_obj['n']:
                page_n = page_obj['n'].decode('utf-8', 'ignore')
                cite += u" [page %s] " % page_n
#                bytes = '&'.join(['byte=%d' % int(byte) for byte in i.bytes])
#                page_href = u'<a href="%s&doc_page=%s&">' % (doc_href,page_n)
#                cite += u", %spage %s.</a>" % (page_href, page_n)
    

#    cite += u" (%s)" % i.pos
    

    cite += "</span>"
    return cite

def make_abs_doc_cite(db,i):
    """ Returns a representation of a PhiloLogic object suitable for a bibliographic report. """
    doc_href = make_absolute_object_link(db,i.philo_id[:1], i.bytes)
    record = u"%s, <i><a href='%s'>%s</a></i> [%s]" % (i.author, doc_href,i.title, i.date)
    if db.locals['debug'] == True:
        record += " %s" % i.filename
    return record

### LINKING ###

def hit_to_link(db,hit):
    ## We should remove this function, it has been superseded.
    i = 0
    partial = []
    best = []
    for n,k in enumerate(hit):
        partial.append(k)
        if partial in db.toms and db.toms[partial]["philo_name"] != "__philo_virtual":
            best = partial[:]
        else:
            break
    return "./" + "/".join(str(b) for b in best)
