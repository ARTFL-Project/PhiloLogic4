#!/usr/bin/env python

import sys
sys.path.append('..')
import os
import re
import functions as f
from lxml import etree
from philologic.DB import DB
from functions.wsgi_handler import WSGIHandler
from wsgiref.handlers import CGIHandler
from functions.ObjectFormatter import convert_entities, valid_html_tags, xml_to_html_class, note_content
from concordance import citation_links
from bibliography import biblio_citation
try:
    import ujson as json
except ImportError:
    print >> sys.stderr, "Import Error, please install ujson for better performance"
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
    philo_id = obj.philo_id
    while obj['philo_name'] == '__philo_virtual' and obj["philo_type"] != "div1":
        philo_id.pop()
        obj = db[philo_id]
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response('200 OK',headers)
    text_object = generate_text_object(obj, db, request, config)
    yield json.dumps(text_object)

def generate_text_object(obj, db, q, config, note=False):
    philo_id = list(obj.philo_id)
    while philo_id[-1] == 0:
        philo_id.pop()
    text_object = {"query": dict([i for i in q]), "philo_id": ' '.join([str(i) for i in philo_id])}
    text_object['prev'] = neighboring_object_id(db, obj.prev)
    text_object['next'] = neighboring_object_id(db, obj.next)
    metadata_fields = {}
    for metadata in db.locals['metadata_fields']:
        if db.locals['metadata_types'][metadata] == "doc":
            metadata_fields[metadata] = obj[metadata]
    text_object['metadata_fields'] = metadata_fields
    citation_hrefs = citation_links(db, config, obj)
    citation = biblio_citation(obj, citation_hrefs)
    text_object['citation'] = citation
    text, imgs = get_text_obj(obj, config, q, db.locals['word_regex'], note=note)
    text_object['text'] = text
    text_object['imgs'] = imgs
    return text_object

def neighboring_object_id(db, philo_id):
    if not philo_id:
        return ''
    philo_id = philo_id.split()[:7]
    while philo_id[-1] == '0':
        philo_id.pop()
    philo_id = str(" ".join(philo_id))
    obj = db[philo_id]
    if obj['philo_name'] == '__philo_virtual' and obj["philo_type"] != "div1":
        # Remove the last number (1) in the philo_id and point to one object level lower
        philo_id = ' '.join(philo_id.split()[:-1])
    return philo_id


def get_text_obj(obj, config, q, word_regex, note=False):
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

    formatted_text, imgs = format_text_object(obj, raw_text, config, q, word_regex, bytes=bytes, note=note)
    formatted_text = formatted_text.decode("utf-8","ignore")
    return formatted_text, imgs

def format_text_object(obj, text, config, q, word_regex, bytes=[], note=False):
    philo_id = obj.philo_id
    if bytes:
        new_text = ""
        last_offset = 0
        for b in bytes:
            new_text += text[last_offset:b] + "<philoHighlight/>"
            last_offset = b
        text = new_text + text[last_offset:]
    first_img = ''
    current_obj_img = []
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
                el.attrib["id"] = target.replace('#', '') + '-link-back'
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
            elif el.tag == "note":
                if el.getparent().attrib["type"] != "notes": ## inline notes
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
                else: # endnotes
                    el.tag = "div"
                    el.attrib['class'] = "xml-note"
                    note_id = '#' + el.attrib['id']
                    link_back = etree.Element("a")
                    link_back.attrib['note-link-back'] = f.link.make_absolute_query_link(config, q, script_name="/scripts/get_note_link_back.py",
                                                                               doc_id=str(philo_id[0]), note_id=note_id)
                    link_back.attrib['class'] = "btn btn-xs btn-default link-back"
                    link_back.attrib['role'] = "button"
                    link_back.text = "Go back to text"
                    el.append(link_back)
            elif el.tag == "item":
                el.tag = "li"
            elif el.tag == "ab" or el.tag == "ln":
                el.tag = "l"
            elif el.tag == "pb" and "n" in el.attrib:
                if "fac" in el.attrib or "id" in el.attrib:
                    if "fac" in el.attrib:
                        img = el.attrib["fac"]
                    else:
                        img = el.attrib["id"]
                    current_obj_img.append(img)
                    el.tag = "p"
                    el.append(etree.Element("a"))
                    el[-1].attrib["href"] = config.page_images_url_root + '/' + img
                    el[-1].text = "[page " + el.attrib["n"] + "]"
                    el[-1].attrib['class'] = "page-image-link"
                    el[-1].attrib['data-gallery'] = ''
            elif el.tag == "figure":
                if el[0].tag == "graphic":
                    img_url = el[0].attrib["url"].replace(":","_")
                    volume = re.match("\d+", img_url).group()
                    url_prefix = config.page_images_url_root + '/V' + volume + "/plate_"
                    el.tag = "span"
                    el.attrib["href"] = url_prefix + img_url + ".jpeg"
                    el[0].tag = "img"
                    el[0].attrib["src"] = url_prefix + img_url + ".sm.jpeg"
                    el[0].attrib["class"] = "inline-img"
                    el.attrib["class"] = "inline-img-container"
                    del el[0].attrib["url"]
                    clear_float = etree.Element("span")
                    clear_float.attrib['style'] = 'clear:both;'
                    el[0].append(clear_float)
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
    output = convert_entities(output.decode('utf-8', 'ignore')).encode('utf-8')

    if note: ## Notes don't need to fetch images
        return (output, {})

    ## Page images
    output, img_obj = page_images(config, output, current_obj_img, philo_id)

    return output, img_obj


def page_images(config, output, current_obj_img, philo_id):
    # first get first page info in case the object doesn't start with a page tag
    first_page_object = get_first_page(philo_id, config)
    if not current_obj_img:
        current_obj_img.append('')
    if first_page_object['byte_start'] and current_obj_img[0] != first_page_object['filename']:
        if first_page_object['filename']:
            page_href = config.page_images_url_root + '/' + first_page_object['filename']
            output = '<p><a href="' + page_href + '" class="page-image-link" data-gallery>[page ' + str(first_page_object["n"]) + "]</a></p>" + output
            if current_obj_img[0] == '':
                current_obj_img[0] = first_page_object['filename']
            else:
                current_obj_img.insert(0, first_page_object['filename'])
        else:
            output = '<p class="page-image-link">[page ' + str(first_page_object["n"]) + "]</p>" + output
    ## Fetch all remainging imgs in document
    all_imgs = get_all_page_images(philo_id, config, current_obj_img)
    img_obj = {'all_imgs': all_imgs, 'current_obj_img': current_obj_img}
    return output, img_obj


def get_first_page(philo_id, config):
    """This function will fetch the first page of any given text object in case there's no <pb>
    starting the object"""
    db = DB(config.db_path + '/data/')
    c = db.dbh.cursor()
    c.execute('select byte_start, byte_end from toms where philo_id="%s"' % ' '.join([str(i) for i in philo_id]))
    result = c.fetchone()
    byte_start = result['byte_start']
    approx_id = str(philo_id[0]) + ' 0 0 0 0 0 0 %'
    try:
        c.execute('select * from pages where philo_id like ? and end_byte >= ? limit 1', (approx_id, byte_start))
    except:
        return {'filename': '', 'byte_start': ''}
    page_result = c.fetchone()
    try:
        filename = page_result['img']
        n = page_result['n'] or ''
        page = {'filename': filename, "n": n, 'byte_start': page_result['start_byte'], 'byte_end': page_result['end_byte']}
    except:
        page = {'filename': '', 'byte_start': ''}
    return page

def get_all_page_images(philo_id, config, current_obj_imgs):
    if current_obj_imgs[0]:
        # We know there are images
        db = DB(config.db_path + '/data/')
        c = db.dbh.cursor()
        approx_id = str(philo_id[0]) + ' 0 0 0 0 0 0 %'
        c.execute('select * from pages where philo_id like ? and img is not null and img != ""', (approx_id,))
        current_obj_imgs = set(current_obj_imgs)
        all_imgs = [i['img'] for i in c.fetchall()]
        return all_imgs
    else:
        return []

if __name__ == "__main__":
    CGIHandler().run(navigation)
