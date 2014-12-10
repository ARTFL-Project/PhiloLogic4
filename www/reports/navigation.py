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
from functions.ObjectFormatter import convert_entities, valid_html_tags, xml_to_html_class
from functions.FragmentParser import parse
from philologic import HitWrapper
from bibliography import biblio_citation
import json

philo_types = set(['div1', 'div2', 'div3'])

def navigation(environ,start_response):
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    obj = db[request.path_components]
    headers = [('Content-type', 'text/html; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response('200 OK',headers)
    if obj.philo_type == 'doc':
        return render_toc(obj, db, request, config)
    else:
        return render_text_object(obj, db, request, config)
    
def render_toc(obj, db, q, config):
    toc_object = generate_toc_object(obj, db, q, config)
    return f.render_template(toc=toc_object,query_string=q.query_string, config=config,template_name='t_o_c.mako', report="t_o_c")

def render_text_object(obj, db, q, config):
    text_object = generate_text_object(obj, db, q, config)
    get_text_object = f.link.make_absolute_query_link(config, q, script_name="/scripts/get_text_object.py")
    get_table_of_contents = f.link.make_absolute_query_link(config, q, script_name="/scripts/get_table_of_contents.py")
    ajax_scripts = {"get_text_object": get_text_object, "get_table_of_contents": get_table_of_contents}
    return f.render_template(text_object=text_object, query_string=q.query_string, obj=obj, ajax=ajax_scripts, config=config,
                             template_name='text_object.mako', report="navigation")

def nav_query(obj,db):
    conn = db.dbh
    c = conn.cursor()
    doc_id =  int(obj.philo_id[0])
    next_doc_id = doc_id + 1
    # find the starting rowid for this doc
    c.execute('select rowid from toms where philo_id="%d 0 0 0 0 0 0"' % doc_id)
    start_rowid = c.fetchone()[0]
    # find the starting rowid for the next doc
    c.execute('select rowid from toms where philo_id="%d 0 0 0 0 0 0"' % next_doc_id)
    try:
        end_rowid = c.fetchone()[0]
    except TypeError: # if this is the last doc, just get the last rowid in the table.
        c.execute('select max(rowid) from toms;')
        end_rowid = c.fetchone()[0]

    # use start_rowid and end_rowid to fetch every div in the document.
    c.execute("select * from toms where rowid >= ? and rowid <=? and philo_type>='div' and philo_type<='div3'", (start_rowid, end_rowid))
    for o in c.fetchall():
        id = [int(n) for n in o["philo_id"].split(" ")]
        i = HitWrapper.ObjectWrapper(id,db,row=o)
        yield i

def generate_toc_object(obj, db, q, config):
    """This function fetches all philo_ids for div elements within a doc"""
    toms_object = nav_query(obj, db)
    text_hierarchy = []
    for i in toms_object:
        if i['philo_name'] == '__philo_virtual' and i["philo_type"] != "div1":
            continue
        else:
            philo_id = i['philo_id']
            philo_type = i['philo_type']
            display_name = ""
            if i['philo_name'] == "front":
                display_name = "Front Matter"
            else:
                display_name = i['head']
                if display_name:
                    display_name = display_name.strip()
                if not display_name:
                    if i["type"] and i["n"]:
                        display_name = i['type'] + " " + i["n"]                       
                    else:
                        display_name = i["head"] or i['type'] or i['philo_name'] or i['philo_type']
            display_name = display_name[0].upper() + display_name[1:]
            link = f.make_absolute_object_link(config, philo_id.split()[:7])
            toc_element = {"philo_id": philo_id, "philo_type": philo_type, "display_name": display_name, "link": link}
            text_hierarchy.append(toc_element)
    metadata_fields = {}
    for metadata in db.locals['metadata_fields']:
        if db.locals['metadata_types'][metadata] == "doc":
            metadata_fields[metadata] = obj[metadata]
    doc_link = {'doc': f.make_absolute_object_link(config,obj.philo_id[:1])}
    citation = biblio_citation(obj, doc_link)
    toc_object = {"query": dict([i for i in q]), "philo_id": obj.philo_id[0], "toc": text_hierarchy, "metadata_fields": metadata_fields,
                  "citation": citation}
    return toc_object

def format_text_object(text,bytes=[]):
    parser = etree.XMLParser(recover=True)
    if bytes:
        new_text = ""
        last_offset = 0
        for b in bytes:
            new_text += text[last_offset:b] + "<philoHighlight/>"
            last_offset = b
        text = new_text + text[last_offset:]
    text = "<div>" + text + "</div>"
    xml = parse(text)
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
            elif el.tag == "note":
                el.tag = 'span'
                el.attrib['class'] = "note-content"
                for child in el:
                    child = note_content(child)
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
                word_match = re.match(r"\w+", el.tail, re.U)
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

def check_philo_virtual(db, path_components):
    """Keep around for reference"""
    object_type = ''
    if len(path_components) == 2:
        object_type = "div1"
    if len(path_components) == 3:
        object_type = "div2"
    if len(path_components) == 4:
        object_type = "div3"
    c = db.dbh.cursor()
    query = 'select philo_name from toms where philo_id like "' + ' '.join(path_components) + ' %" and philo_type="' + object_type + '"'
    c.execute(query)
    try:
        name = c.fetchone()[0]
        if name == "__philo_virtual":
            return True
        else:
            return False
    except TypeError:
        return False

def generate_text_object(obj, db, q, config):
    text_object = {"query": dict([i for i in q]), "philo_id": obj.philo_id[0]}
    text_object['prev'] = ' '.join(obj.prev.split()[:7])
    text_object['next'] = ' '.join(obj.next.split()[:7])
    metadata_fields = {}
    for metadata in db.locals['metadata_fields']:
        if db.locals['metadata_types'][metadata] == "doc":
            metadata_fields[metadata] = obj[metadata]
    text_object['metadata_fields'] = metadata_fields
    doc_link = {'doc': f.make_absolute_object_link(config,obj.philo_id[:1])}
    citation = biblio_citation(obj, doc_link)
    text_object['citation'] = citation
    text = get_text_obj(obj, config.db_path, query_args=q['byte'])
    text_object['text'] = text
    return text_object

def get_text_obj(obj, path, query_args=False):
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

    if query_args:
        bytes = sorted([int(byte) - byte_start for byte in query_args.split('+')])
    else:
        bytes = []
        
    formatted = format_text_object(raw_text,bytes).decode("utf-8","ignore")
    return formatted
