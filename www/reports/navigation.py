#!/usr/bin/env python

import sys
sys.path.append('..')
import os
import sqlite3
import re
import functions as f
from lxml import etree
from philologic.DB import DB
from functions.wsgi_handler import WSGIHandler
from wsgiref.handlers import CGIHandler
from functions.ObjectFormatter import convert_entities, valid_html_tags, xml_to_html_class
from functions.FragmentParser import parse
from philologic import HitWrapper
from concordance import citation_links
from bibliography import biblio_citation
try:
    import simplejson as json
except ImportError:
    print >> sys.stderr, "Import Error, please install simplejson for better performance"
    import json

philo_types = set(['div1', 'div2', 'div3'])
philo_slices = {"doc": 1, "div1": 2, "div2": 3, "div3": 4, "para": 5}

def navigation(environ,start_response):
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    try:
        obj = db[request.philo_id]
    except ValueError:
        philo_id = ' '.join(request.path_components)
        obj = db[philo_id]
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response('200 OK',headers)
    text_object = generate_text_object(obj, db, request, config)
    yield json.dumps(text_object)

def generate_text_object(obj, db, q, config):
    philo_id = list(obj.philo_id)
    while philo_id[-1] == 0:
        philo_id.pop()
    text_object = {"query": dict([i for i in q]), "philo_id": ' '.join([str(i) for i in philo_id])}
    text_object['prev'] = ' '.join(obj.prev.split()[:7][:philo_slices[obj.philo_type]])
    text_object['next'] = ' '.join(obj.next.split()[:7][:philo_slices[obj.philo_type]])
    metadata_fields = {}
    for metadata in db.locals['metadata_fields']:
        if db.locals['metadata_types'][metadata] == "doc":
            metadata_fields[metadata] = obj[metadata]
    text_object['metadata_fields'] = metadata_fields
    citation_hrefs = citation_links(db, config, obj)
    citation = biblio_citation(obj, citation_hrefs)
    text_object['citation'] = citation
    text = get_text_obj(obj, config, q, db.locals['word_regex'])
    text_object['text'] = text
    return text_object

def get_text_obj(obj, config, q, word_regex):
    path = config.db_path
    filename = obj.doc.filename
    if filename and os.path.exists(path + "/data/TEXT/" + filename):
        path += "/data/TEXT/" + filename
    else:
        ## workaround for when no filename is returned with the full philo_id of the object
        philo_id = obj.philo_id[0] + ' 0 0 0 0 0 0'
        c = obj.db.dbh.cursor()
        c.execute("select filename from toms where philo_type='doc' and philo_id =? limit 1", (philo_id,))
        path += "/data/TEXT/" + c.fetchone()["filename"]
    file = open(path)
    byte_start = int(obj.byte_start)
    file.seek(byte_start)
    width = int(obj.byte_end) - byte_start
    raw_text = file.read(width)
    try:
        bytes = sorted([int(byte) - byte_start for byte in q.byte])
    except ValueError: ## q.byte contains an empty string
        bytes = []
        
    formatted = format_text_object(raw_text, config, q, word_regex, bytes=bytes).decode("utf-8","ignore")
    return formatted

def format_text_object(text, config, q, word_regex, bytes=[]):
    if bytes:
        new_text = ""
        last_offset = 0
        for b in bytes:
            new_text += text[last_offset:b] + "<philoHighlight/>"
            last_offset = b
        text = new_text + text[last_offset:]
    text = "<div>" + text + "</div>"
    xml = f.FragmentParser.parse(text)
    for el in xml.iter():        
        try:
            if el.tag == "sc" or el.tag == "scx":
                el.tag = "span"
                el.attrib["class"] = "small-caps"
            elif el.tag == "head":
                el.tag = "b"
                el.attrib["class"] = "headword"
                el.append(etree.Element("br"))
            elif el.tag == "list":
                el.tag = "ul"
            elif el.tag == "title":
                el.tag = "span"
                el.attrib['class'] = "xml-title"
            elif el.tag == "q":
                el.tag = "span"
                el.attrib['class'] = 'xml-q'
            elif el.tag == "ptr" or el.tag == "ref":
                target = el.attrib["target"]
                link = f.link.make_absolute_query_link(config, q, script_name="/scripts/get_notes.py", target=target)
                el.attrib["data-ref"] = link
                del el.attrib["target"]
                el.attrib['class'] = "note-ref"
                el.attrib['tabindex'] = "0"
                el.attrib['data-toggle'] = "popover"
                el.attrib['data-container'] = "body"
                el.attrib["data-placement"] = "right"
                el.attrib["data-trigger"] = "focus"
                el.attrib["data-html"] = "true"
                el.attrib["data-animation"] = "true"
                el.text = "note"
                el.tag = "span"
            elif el.tag == "note" and el.getparent().attrib["type"] != "notes":
                el.tag = 'span'
                el.attrib['class'] = "note-content"
                for child in el:
                    child = note_content(child)
                # insert an anchor before this element by scanning through the parent
                parent = el.getparent()
                for i,child in enumerate(parent):
                    if child == el:
                        attribs = {"class":"note", "tabindex": "0", "data-toggle": "popover", "data-container": "body",
                                   "data-placement": "right", "data-trigger": "focus"}
                        parent.insert(i,etree.Element("a",attrib=attribs))
                        new_anchor = parent[i]
                        new_anchor.text = "note"

            elif el.tag == "item":
                el.tag = "li"
            elif el.tag == "ab" or el.tag == "ln":
                el.tag = "l"
            elif el.tag == "pb" and "fac" in el.attrib and "n" in el.attrib:
                el.tag = "p"
                el.append(etree.Element("a"))
                el[-1].attrib["href"] = 'http://artflx.uchicago.edu/images/encyclopedie/' + el.attrib["fac"]
                el[-1].text = "[page " + el.attrib["n"] + "]"
                el[-1].attrib['class'] = "page-image-link"
                el[-1].attrib['data-gallery'] = ''
            elif el.tag == "figure":
                if el[0].tag == "graphic":
                    img_url = el[0].attrib["url"].replace(":","_")
                    volume = re.match("\d+",img_url).group()
                    url_prefix = "http://artflx.uchicago.edu/images/encyclopedie/V" + volume + "/plate_"
                    el.tag = "a"
                    el.attrib["href"] = url_prefix + img_url + ".jpeg"
                    el[0].tag = "img"
                    el[0].attrib["src"] = url_prefix + img_url + ".sm.jpeg"
                    el[0].attrib["class"] = "plate_img"
                    el.attrib["class"] = "plate-image-link"
                    el.attrib['data-gallery'] = ''
                    del el[0].attrib["url"]
                    el.append(etree.Element("br"))
            elif el.tag == "philoHighlight":        
                word_match = re.match(word_regex, el.tail, re.U)
                if word_match:
                    el.text = el.tail[:word_match.end()]
                    el.tail = el.tail[word_match.end():]
                el.tag = "span"
                el.attrib["class"] = "highlight"
            if el.tag not in valid_html_tags:
                el = xml_to_html_class(el)
        except:
            pass
    output = etree.tostring(xml)
    ## remove spaces around hyphens and apostrophes
    output = re.sub(r" ?([-';.])+ ", '\\1 ', output)
    return convert_entities(output.decode('utf-8', 'ignore')).encode('utf-8')

if __name__ == "__main__":
    CGIHandler().run(navigation)
