#!/usr/bin/env python
import htmlentitydefs
import re
import sqlite3

from lxml import etree
from philologic.DB import DB
from philologic.utils import convert_entities

import FragmentParser
from link import *

begin_match = re.compile(r'^[^<]*?>')
start_cutoff_match = re.compile(r'^[^ <]+')
end_match = re.compile(r'<[^>]*?\Z')
space_match = re.compile(r" ?([-'])+ ")
term_match = re.compile(r"\w+", re.U)
strip_start_punctuation = re.compile("^[,?;.:!']")

# Source: https://developer.mozilla.org/en-US/docs/Web/Guide/HTML/HTML5/HTML5_element_list
valid_html_tags = set(
    ['html', 'head', 'title', 'base', 'link', 'meta', 'style', 'script', 'noscript', 'template', 'body', 'section',
     'nav', 'article', 'aside', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header', 'footer', 'address', 'main', 'p',
     'hr', 'pre', 'blockquote', 'ol', 'ul', 'li', 'dl', 'dt', 'dd', 'figure', 'figcaption', 'div', 'a', 'em', 'strong',
     'small', 's', 'cite', 'q', 'dfn', 'abbr', 'data', 'time', 'code', 'var', 'samp', 'kbd', 'sub', 'sup', 'i', 'b',
     'u', 'mark', 'ruby', 'rt', 'rp', 'bdi', 'bdo', 'span', 'br', 'wbr', 'ins', 'del', 'img', 'iframe', 'embed',
     'object', 'param', 'video', 'audio', 'source', 'track', 'canvas', 'map', 'area', 'svg', 'math', 'table', 'caption',
     'colgroup', 'col', 'tbody', 'thead', 'tfoot', 'tr', 'td', 'th', 'form', 'fieldset', 'legend', 'label', 'input',
     'button', 'select', 'datalist', 'optgroup', 'option', 'textarea', 'keygen', 'output', 'progress', 'meter',
     'details', 'summary', 'menuitem', 'menu'])


def get_all_text(element):
    text = ""
    text += element.text
    for child in element:
        text += get_all_text(child)
        text += child.tail
    return text


def xml_to_html_class(element):
    old_tag = element.tag[:]
    if element.tag == "div1" or element.tag == "div2" or element.tag == "div3":
        element.tag = "div"
    else:
        element.tag = "span"
    element.attrib['class'] = "xml-%s" % old_tag
    return element


def note_content(element):
    if element.tag != "philoHighlight":
        element = xml_to_html_class(element)
    for child in element:
        child = note_content(child)
    return element


def adjust_bytes(bytes, padding):
    """Readjust byte offsets for concordance"""
    ### Called from every report that fetches text and needs highlighting
    #    bytes = sorted(bytes) # bytes aren't stored in order
    start_byte = bytes[0] - padding
    first_hit = bytes[0] - start_byte
    if start_byte < 0:
        first_hit = first_hit + start_byte  ## this is a subtraction really
        start_byte = 0
    new_bytes = []
    for pos, word_byte in enumerate(bytes):
        if pos == 0:
            new_bytes.append(first_hit)
        else:
            new_bytes.append(word_byte - start_byte)
    return new_bytes, start_byte


def format_concordance(text, word_regex, bytes=[]):
    word_regex = "\w+" # text is converted to unicode so we use the \w boundary to match
    removed_from_start = 0
    begin = begin_match.search(text)
    if begin:
        removed_from_start = len(begin.group(0))
        text = text[begin.end(0):]
    start_cutoff = start_cutoff_match.search(text)
    if start_cutoff:
        removed_from_start += len(start_cutoff.group(0))
        text = text[start_cutoff.end(0):]
    end = end_match.search(text)
    if end:
        text = text[:end.start(0)]
    if bytes:
        bytes = [b - removed_from_start for b in bytes]
        new_text = ""
        last_offset = 0
        for b in bytes:
            if b > 0 and b < len(text):
                new_text += text[last_offset:b] + "<philoHighlight/>"
                last_offset = b
        text = new_text + text[last_offset:]
    xml = FragmentParser.parse(text)
    allowed_tags = set(['philoHighlight', 'l', 'ab', 'ln', 'w', 'sp', 'speaker', 'stage', 'i', 'sc', 'scx', 'br'])
    text = u''
    for el in xml.iter():
        if el.tag.startswith("DIV"):
            el.tag = el.tag.lower()
        if el.tag not in allowed_tags:
            el.tag = 'span'
        elif el.tag == "ab" or el.tag == "ln":
            el.tag = "l"
        elif el.tag == "title":
            el.tag = "span"
            el.attrib['class'] = "xml-title"
        elif el.tag == "q":
            el.tag = "span"
            el.attrib['class'] = 'xml-q'
        if "id" in el.attrib:  ## kill ids in order to avoid the risk of having duplicate ids in the HTML
            del el.attrib["id"]
        if el.tag == "sc" or el.tag == "scx":
            el.tag = "span"
            el.attrib["class"] = "small-caps"
        elif el.tag == "img":  # Remove img elements from parent in concordances
            el.getparent().remove(el)
        if el.tag == "philoHighlight":
            word_match = re.match(word_regex, el.tail, re.U)
            if word_match:
                el.text = el.tail[:word_match.end()]
                el.tail = el.tail[word_match.end():]
            el.tag = "span"
            el.attrib["class"] = "highlight"
        if el.tag not in valid_html_tags:
            el = xml_to_html_class(el)
    output = etree.tostring(xml)
    output = re.sub(r'\A<div class="philologic-fragment">', '', output)
    output = re.sub(r'</div>\Z', '', output)
    ## remove spaces around hyphens and apostrophes
    output = space_match.sub('\\1', output)
    output = convert_entities(output)
    output = strip_start_punctuation.sub("", output)
    return output


def format_strip(text, bytes=[]):
    """Remove formatting for HTML rendering
    Called from: -kwic.py
                 -frequency.py"""
    removed_from_start = 0
    begin = begin_match.search(text)
    if begin:
        removed_from_start = len(begin.group(0))
        text = text[begin.end(0):]
    start_cutoff = start_cutoff_match.search(text)
    if start_cutoff:
        removed_from_start += len(start_cutoff.group(0))
        text = text[start_cutoff.end(0):]
    end = end_match.search(text)
    if end:
        text = text[:end.start(0)]
    if bytes:
        bytes = [b - removed_from_start for b in bytes]
        new_text = ""
        last_offset = 0
        for b in bytes:
            if b > 0 and b < len(text):
                new_text += text[last_offset:b] + "<philoHighlight/>"
                last_offset = b
        text = new_text + text[last_offset:]
    xml = FragmentParser.parse(text)
    output = clean_tags(xml)
    ## remove spaces around hyphens and apostrophes
    output = space_match.sub('\\1', output)
    return output


def format_text_object(obj, text, config, request, word_regex, bytes=[], note=False):
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
    xml = FragmentParser.parse(text)
    c = obj.db.dbh.cursor()
    for el in xml.iter():
        try:
            if el.tag.startswith("DIV"):
                el.tag = el.tag.lower()
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
            elif el.tag == "ref":
                if el.attrib["type"] == "note":
                    target = el.attrib["target"]
                    link = make_absolute_query_link(config, request, script_name="/scripts/get_notes.py", target=target)
                    if "n" in el.attrib:
                        el.text = el.attrib["n"]
                    else:
                        el.text = "note"
                    el.tag = "span"
                    el.attrib["data-ref"] = link
                    el.attrib["id"] = target.replace('#', '') + '-link-back'
                    del el.attrib["target"]
                    # attributes for popover note
                    el.attrib['class'] = "note-ref"
                    el.attrib['tabindex'] = "0"
                    el.attrib['data-toggle'] = "popover"
                    el.attrib['data-container'] = "body"
                    el.attrib["data-placement"] = "right"
                    el.attrib["data-trigger"] = "focus"
                    el.attrib["data-html"] = "true"
                    el.attrib["data-animation"] = "true"
            elif el.tag == "note":
                # endnotes
                in_end_note = False
                for div in el.iterancestors(tag="div"):
                    if div.attrib["type"] == "notes":
                        in_end_note = True
                        break
                if in_end_note:
                    el.tag = "div"
                    el.attrib['class'] = "xml-note"
                    link_back = etree.Element("a")
                    c.execute('select parent, start_byte from refs where target=? and parent like ?',
                              (el.attrib['id'], str(philo_id[0]) + " %"))
                    object_id, start_byte = c.fetchone()
                    link_back.attrib['href'] = 'navigate/%s%s' % ('/'.join(object_id.split()[:2]),
                                                                  '#%s-link-back' % el.attrib['id'])
                    link_back.attrib['class'] = "btn btn-xs btn-default link-back"
                    link_back.attrib['role'] = "button"
                    link_back.text = "Go back to text"
                    el.append(link_back)
                else:  ## inline notes
                    el.tag = 'span'
                    el.attrib['class'] = "note-content"
                    for child in el:
                        child = note_content(child)
                    # insert an anchor before this element by scanning through the parent
                    parent = el.getparent()
                    for i, child in enumerate(parent):
                        if child == el:
                            attribs = {"class": "note",
                                       "tabindex": "0",
                                       "data-toggle": "popover",
                                       "data-container": "body",
                                       "data-placement": "right",
                                       "data-trigger": "focus"}
                            parent.insert(i, etree.Element("a", attrib=attribs))
                            new_anchor = parent[i]
                            new_anchor.text = "note"
            elif el.tag == "item":
                el.tag = "li"
            elif el.tag == "ab" or el.tag == "ln":
                el.tag = "l"
            elif el.tag == "img":
                el.attrib["onerror"] = "this.style.display='none'"
            elif el.tag == "pb" and "n" in el.attrib:
                if "fac" in el.attrib or "id" in el.attrib:
                    if "fac" in el.attrib:
                        img = el.attrib["fac"]
                    else:
                        img = el.attrib["id"]
                    current_obj_img.append(img)
                    el.tag = "span"
                    el.attrib["class"] = "xml-pb-image"
                    el.append(etree.Element("a"))
                    el[-1].attrib["href"] = config.page_images_url_root + '/' + img + config.page_image_extension
                    el[-1].text = "[page " + el.attrib["n"] + "]"
                    el[-1].attrib['class'] = "page-image-link"
                    el[-1].attrib['data-gallery'] = ''
            elif el.tag == "figure":
                if el[0].tag == "graphic":
                    img_url = el[0].attrib["url"].replace(":", "_")
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
        except Exception as e:
            import sys
            print >> sys.stderr, e
            pass
    output = etree.tostring(xml)
    ## remove spaces around hyphens and apostrophes
    output = re.sub(r" ?([-';.])+ ", '\\1 ', output)
    output = convert_entities(output.decode('utf-8', 'ignore')).encode('utf-8')

    if note:  ## Notes don't need to fetch images
        return (output, {})

    ## Page images
    output, img_obj = page_images(config, output, current_obj_img, philo_id)

    return output, img_obj


def page_images(config, output, current_obj_img, philo_id):
    # first get first page info in case the object doesn't start with a page tag
    first_page_object = get_first_page(philo_id, config)
    if not current_obj_img:
        current_obj_img.append('')
    if first_page_object['start_byte'] and current_obj_img[0] != first_page_object['filename']:
        if first_page_object['filename']:
            page_href = config.page_images_url_root + '/' + first_page_object['filename'] + config.page_image_extension
            output = '<p><a href="' + page_href + '" class="page-image-link" data-gallery>[page ' + str(
                first_page_object["n"]) + "]</a></p>" + output
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
    if len(philo_id) < 9:
        c.execute('select start_byte, end_byte from toms where philo_id="%s"' % ' '.join([str(i) for i in philo_id]))
        result = c.fetchone()
        start_byte = result['start_byte']
        approx_id = str(philo_id[0]) + ' 0 0 0 0 0 0 %'
        try:
            c.execute('select * from pages where philo_id like ? and end_byte >= ? limit 1', (approx_id, start_byte))
        except:
            return {'filename': '', 'start_byte': ''}
    else:
        c.execute('select * from pages where philo_id like ? limit 1', (' '.join([str(i) for i in philo_id]), ))
    page_result = c.fetchone()
    try:
        filename = page_result['img']
        n = page_result['n'] or ''
        page = {'filename': filename,
                "n": n,
                'start_byte': page_result['start_byte'],
                'end_byte': page_result['end_byte']}
    except:
        page = {'filename': '', 'start_byte': ''}
    return page


def get_all_page_images(philo_id, config, current_obj_imgs):
    if current_obj_imgs[0]:
        # We know there are images
        db = DB(config.db_path + '/data/')
        c = db.dbh.cursor()
        approx_id = str(philo_id[0]) + ' 0 0 0 0 0 0 %'
        try:
            c.execute('select * from pages where philo_id like ? and img is not null and img != ""', (approx_id, ))
            current_obj_imgs = set(current_obj_imgs)
            all_imgs = [i['img'] for i in c.fetchall()]
        except sqlite3.OperationalError:
            all_imgs = []
        return all_imgs
    else:
        return []


def clean_tags(element):
    text = u''
    for child in element:
        text += clean_tags(child)
    if element.tag == "philoHighlight":
        word_match = term_match.match(convert_entities(element.tail))
        if word_match:
            return '<span class="highlight">' + element.text + text + element.tail[:word_match.end(
            )] + "</span>" + element.tail[word_match.end():]
        text = element.text + text + element.tail
        return '<span class="highlight">' + element.text + text + "</span>" + element.tail
    return element.text + text + element.tail
