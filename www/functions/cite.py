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
    section_name = section_names[0] or "Section"
    try:
        sub_section_name = section_names[1] or ""
    except IndexError:
        sub_section_name = ""
    title = '<a href="%s">%s</a>' % (doc_href, i.doc.title.strip())
    author = i.doc.author
    if author:
        citation = "%s <i>%s</i>" % (author.strip(),title)
    else:
        citation = "<i>%s</i>" % title
    date = i.doc.date
    if date:
        try:
            citation += " [%s]" % str(date)
        except:
            pass
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
    citation = u'<span class="philologic_cite">' + citation + "</span>"
    return citation

def biblio_citation(db, config, i):
    """ Returns a representation of a PhiloLogic object suitable for a bibliographic report. """
    doc_href = make_absolute_object_link(config,i.philo_id[:1], i.bytes)
    author = i.doc.author
    if author:
        record = u"%s, <i><a href='%s'>%s</a></i>" % (i.doc.author, doc_href,i.doc.title)
    else:
        record = u"<i><a href='%s'>%s</a></i>" % (doc_href,i.doc.title)
    date = i.doc.date
    if date:
        try:
            record += " [<b>%s</b>] " % date
        except:
            pass
    more_metadata = []
    collection = i.doc.collection
    if collection:
        more_metadata.append(collection)
    publisher = i.doc.publisher
    if publisher:
        more_metadata.append(publisher)
    pub_place = i.doc.pub_place
    if pub_place:
        more_metadata.append(pub_place)
    if more_metadata:
        record += '(%s)' % ', '.join(more_metadata)
    genre = i.doc.text_genre
    if genre:
        record += ' [genre: %s]' % genre
    #if db.locals['debug'] == True:
    #    record += " %s" % i.doc.filename
    return record

def kwic_citation(db, i, short_citation_length):
    full_citation = ""
    short_citation = []
    author = i.doc.author or ''
    if author:
        full_citation += author + ", "
    short_citation.append(author)
    title = i.doc.title
    full_citation += title
    short_citation.append(title)
        
    if len(', '.join([s for s in short_citation if s])) > short_citation_length:
        short_author, short_title = tuple(short_citation)
        if len(short_author) > 10:
            short_author = short_author[:10] + "&#8230;"
            short_citation[0] = short_author
        title_len = short_citation_length - len(short_author)
        if len(short_title) > title_len:
            short_citation[1] = short_title[:title_len]
    short_citation = ', '.join([s for s in short_citation if s])
    
    ## Generate link to a div1 object
    get_query = byte_query(i.bytes)
    href = "./" + '/'.join([str(j) for j in i.div1.philo_id]) + get_query
    
    return full_citation, short_citation, href

def make_abs_doc_cite_mobile(db, i):
    """ Returns a representation of a PhiloLogic object suitable for a bibliographic report. """
    record = u"%s, <i><a data-id='%s' class='biblio_cite'>%s</a></i>" % (i.doc.author, ' '.join([str(j) for j in i.philo_id]),i.doc.title)
    date = i.doc.date
    if date:
        record += " [%s]" % date
    return record

def make_abs_doc_shrtcit_mobile(db, i):
    """ Returns a representation of a PhiloLogic object suitable for a (short) bibliographic report. """
    cmc_author = i.doc.author.split(",", 1)[0]
    section_names = [i.div1.head,i.div2.head,i.div3.head]
    head = section_names[2] or section_names[1] or section_names[0]
    record = cmc_author + ", " + i.doc.title + ": " + head
    return record
    
def make_abs_doc_cite_biblio_mobile(db, i):
    """ Returns a representation of a PhiloLogic object suitable for a bibliographic report. """
    record = u"%s|<i><span class='biblio_cite'>%s</span></i>" % (i.doc.author,i.doc.title)
    date = i.doc.date
    if date:
        record += " [<b>%s</b>] " % date
    more_metadata = []
    collection = i.doc.collection
    if collection:
        more_metadata.append(collection)
    publisher = i.doc.publisher
    if publisher:
        more_metadata.append(publisher)
    pub_place = i.doc.pub_place
    if pub_place:
        more_metadata.append(pub_place)
    if more_metadata:
        record += '(%s)' % ', '.join(more_metadata)
    genre = i.doc.text_genre
    if genre:
        record += ' [genre: %s]' % genre
    return record
