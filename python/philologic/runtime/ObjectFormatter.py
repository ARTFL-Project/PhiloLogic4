#!/usr/bin/env python3
"""Text Object formatter"""


import os
import re
import sqlite3

from lxml import etree
from philologic.DB import DB
from philologic.runtime.FragmentParser import parse as FragmentParserParse
from philologic.runtime.link import make_absolute_query_link
from philologic.utils import convert_entities

BEGIN_MATCH = re.compile(rb'^[^<]*?>')
START_CUTOFF_MATCH = re.compile(rb'^[^ <]+')
END_MATCH = re.compile(rb'<[^>]*?\Z')
SPACE_MATCH = re.compile(r" ?([-'])+ ")
TERM_MATCH = re.compile(r"\w+")
STRIP_START_PUNCTUATION = re.compile(r"^[,?;.:!']")

# Source: https://developer.mozilla.org/en-US/docs/Web/Guide/HTML/HTML5/HTML5_element_list
valid_html_tags = set(
    ['html', 'head', 'title', 'base', 'link', 'meta', 'style', 'script', 'noscript', 'template', 'body', 'section',
     'nav', 'article', 'aside', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header', 'footer', 'address', 'main', 'p', 'hr',
     'pre', 'blockquote', 'ol', 'ul', 'li', 'dl', 'dt', 'dd', 'figure', 'figcaption', 'div', 'a', 'em', 'strong',
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


def format_concordance(text_in_utf8, word_regex, byte_offsets=[]):
    removed_from_start = 0
    begin = BEGIN_MATCH.search(text_in_utf8)
    if begin:
        removed_from_start = len(begin.group(0))
        text_in_utf8 = text_in_utf8[begin.end(0):]
    start_cutoff = START_CUTOFF_MATCH.search(text_in_utf8)
    if start_cutoff:
        removed_from_start += len(start_cutoff.group(0))
        text_in_utf8 = text_in_utf8[start_cutoff.end(0):]
    end = END_MATCH.search(text_in_utf8)
    if end:
        text_in_utf8 = text_in_utf8[:end.start(0)]
    if byte_offsets:
        byte_offsets = [b - removed_from_start for b in byte_offsets]
        new_text = b""
        last_offset = 0
        for b in byte_offsets:
            if b > 0 and b < len(text_in_utf8):
                new_text += text_in_utf8[last_offset:b] + b"<philoHighlight/>"
                last_offset = b
        text_in_utf8 = new_text + text_in_utf8[last_offset:]
    text = text_in_utf8.decode('utf8', 'ignore')
    xml = FragmentParserParse(text)
    allowed_tags = set(['philoHighlight', 'l', 'ab', 'ln', 'w', 'sp', 'speaker', 'stage', 'i', 'sc', 'scx', 'br'])
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
        if "id" in el.attrib and el.tag != "l":  ## kill ids in order to avoid the risk of having duplicate ids in the HTML
            del el.attrib["id"]
        if el.tag == "sc" or el.tag == "scx":
            el.tag = "span"
            el.attrib["class"] = "small-caps"
        elif el.tag == "img":  # Remove img elements from parent in concordances
            el.getparent().remove(el)
        if el.tag == "philoHighlight":
            word_match = re.match(word_regex, el.tail)
            if word_match:
                el.text = el.tail[:word_match.end()]
                el.tail = el.tail[word_match.end():]
            el.tag = "span"
            el.attrib["class"] = "highlight"
        if el.tag not in valid_html_tags:
            el = xml_to_html_class(el)
    output = etree.tostring(xml).decode('utf8', 'ignore')
    output = re.sub(r'\A<div class="philologic-fragment">', '', output)
    output = re.sub(r'</div>\Z', '', output)
    ## remove spaces around hyphens and apostrophes
    output = SPACE_MATCH.sub('\\1', output)
    output = convert_entities(output)
    output = STRIP_START_PUNCTUATION.sub("", output)
    return output


def format_strip(text, word_regex, byte_offsets=None):
    """Remove formatting for HTML rendering
    Called from KWIC only"""
    removed_from_start = 0
    begin = BEGIN_MATCH.search(text)
    if begin:
        removed_from_start = len(begin.group(0))
        text = text[begin.end(0):]
    start_cutoff = START_CUTOFF_MATCH.search(text)
    if start_cutoff:
        removed_from_start += len(start_cutoff.group(0))
        text = text[start_cutoff.end(0):]
    end = END_MATCH.search(text)
    if end:
        text = text[:end.start(0)]
    if byte_offsets is not None:
        byte_offsets = [b - removed_from_start for b in byte_offsets]
        new_text = b""
        last_offset = 0
        for b in byte_offsets:
            if b > 0 and b < len(text):
                new_text += text[last_offset:b] + b"<philoHighlight/>"
                last_offset = b
        text = new_text + text[last_offset:]
    xml = FragmentParserParse(text.decode('utf8', 'ignore'))
    output = clean_tags(xml, word_regex)
    ## remove spaces around hyphens and apostrophes
    output = SPACE_MATCH.sub('\\1', output)
    return output


def format_text_object(obj, text, config, request, word_regex, byte_offsets=None, note=False, images=True):
    """Format text objects"""
    philo_id = obj.philo_id
    if byte_offsets is not None:
        new_text = b""
        last_offset = 0
        for b in byte_offsets:
            new_text += text[last_offset:b] + b"<philoHighlight/>"
            last_offset = b
        text = new_text + text[last_offset:]
    current_obj_img = []
    current_graphic_img = []
    text = "<div>" + text.decode('utf8', 'ignore') + "</div>"
    xml = FragmentParserParse(text)
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
            elif el.tag == "table":
                el.tag = "span"
                el.attrib["class"] = "xml-table"
            elif el.tag == "ref" or el.tag == "xref":
                if el.attrib["type"] == "note" or el.attrib["type"] == "footnote":
                    target = el.attrib["target"]
                    link = make_absolute_query_link(config, request, script_name="/scripts/get_notes.py", target=target)
                    if "n" in el.attrib:
                        el.text = el.attrib["n"]
                    else:
                        el.text = "*"
                    if el.text == "":
                        el.text = "*"
                    el.tag = "span"
                    el.attrib["data-ref"] = link
                    el.attrib["id"] = target.replace('#', '') + '-link-back'
                    # attributes for popover note
                    el.attrib['class'] = "note-ref"
                    el.attrib['tabindex'] = "0"
                    el.attrib['data-toggle'] = "popover"
                    el.attrib['data-container'] = "body"
                    el.attrib["data-placement"] = "right"
                    el.attrib["data-trigger"] = "focus"
                    el.attrib["data-html"] = "true"
                    el.attrib["data-animation"] = "true"
                elif el.attrib["type"] == "cross":
                    c.execute("SELECT philo_id FROM toms WHERE id=? LIMIT 1", (el.attrib["target"],))
                    try:
                        object_id = c.fetchone()[0]
                    except IndexError:
                        el.tag = "span"
                        continue
                    el.tag = "a"
                    el.attrib["href"] = 'navigate/%s' % '/'.join([i for i in object_id.split() if i != "0"])
                    el.attrib["class"] = "xml-ref-cross"
                    del el.attrib["target"]
                elif el.attrib["type"] == "search":
                    metadata, metadata_value = el.attrib["target"].split(':')
                    params = {metadata: metadata_value, "report": "bibliography"}
                    el.tag = "a"
                    el.attrib["href"] = make_absolute_query_link(config, [], **params)
                    del el.attrib["target"]
            elif el.tag == "note":
                # endnotes
                in_end_note = False
                for ancestor in el.iterancestors():
                    if ancestor.tag.startswith('div'):
                        if "type" in ancestor.attrib:
                            if ancestor.attrib["type"] == "notes":
                                in_end_note = True
                                break
                if note:  # in footnote
                    el.tag = "div"
                elif in_end_note:  # in end note
                    el.tag = "div"
                    el.attrib['class'] = "xml-note"
                    link_back = etree.Element("a")
                    c.execute('select parent from refs where target=? and parent like ?',
                              (el.attrib['id'], str(philo_id[0]) + " %"))
                    object_id = c.fetchone()[0]
                    link_back.attrib['href'] = 'navigate/%s%s' % ('/'.join([i for i in object_id.split() if i != "0"]),
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
                el.tag = "span"
                el.attrib["class"] = "xml-pb-image"
                if config.page_images_url_root:
                    if "facs" in el.attrib or "id" in el.attrib:
                        if "facs" in el.attrib:
                            img = el.attrib["facs"]
                        else:
                            img = el.attrib["id"]
                        current_obj_img.append(img.split()[0])
                        el.append(etree.Element("a"))
                        img_split = img.split()
                        el[-1].attrib["href"] = os.path.join(config.page_images_url_root, img_split[0]) + config.page_image_extension
                        if len(img_split) == 2:
                            el[-1].attrib["large-img"] = os.path.join(config.page_images_url_root, img_split[1]) + config.page_image_extension
                        else:
                            el[-1].attrib["large-img"] = os.path.join(config.page_images_url_root, img_split[0]) + config.page_image_extension
                        el[-1].text = "[page " + el.attrib["n"] + "]"
                        if config.external_page_images:
                            el[-1].attrib["target"] = "_blank"
                        else:
                            el[-1].attrib['class'] = "page-image-link"
                            el[-1].attrib['data-gallery'] = ''
                else:
                    if el.attrib["n"]:
                        el.text = "--%s--" % el.attrib["n"]
                    else:
                        el.text = "--na--"
                grand_parent = el.getparent().getparent()
                if grand_parent.attrib["class"] == "xml-row":
                    # Move page outside of table row to avoid display issues
                    tail = etree.Element("span")
                    tail.text = el.tail
                    el.tail = ""
                    great_grand_parent = grand_parent.getparent()
                    grand_parent_index = great_grand_parent.index(grand_parent)
                    el_index = el.getparent().index(el)
                    great_grand_parent.insert(grand_parent_index+1, el)
                    parent.insert(el_index, tail)
            if el.tag == "graphic":
                if config.page_images_url_root:
                    imgs = el.attrib["facs"].split()
                    current_graphic_img.append(imgs[0])
                    el.attrib["src"] = os.path.join(config.page_images_url_root, imgs[0])
                    el.tag = "img"
                    el.attrib["class"] = "inline-img"
                    el.attrib['data-gallery'] = ''
                    el.attrib["inline-img"] = ""
                    if len(imgs) > 1:
                        el.attrib["large-img"] = os.path.join(config.page_images_url_root, imgs[1])
                    else:
                        el.attrib["large-img"] = os.path.join(config.page_images_url_root, imgs[0])
                    del el.attrib["url"]
            elif el.tag == "philoHighlight":
                word_match = re.match(word_regex, el.tail, re.U)
                if word_match:
                    el.text = el.tail[:word_match.end()]
                    el.tail = el.tail[word_match.end():]
                el.tag = "span"
                el.attrib["class"] = "highlight"
            if el.tag not in valid_html_tags:
                el = xml_to_html_class(el)
        except Exception as exception:
            import sys
            print(exception, file=sys.stderr)
            pass
    output = etree.tostring(xml).decode('utf8', 'ignore')
    ## remove spaces around hyphens and apostrophes
    output = re.sub(r" ?([-';.])+ ", '\\1 ', output)
    output = convert_entities(output)

    if note:  ## Notes don't need to fetch images
        return (output, {})
    if not images:
        return (output, {})

    ## Page images
    output, images = page_images(config, output, current_obj_img, current_graphic_img, philo_id)
    return output, images

def page_images(config, output, current_obj_img, current_graphic_img, philo_id):
    """Get page images"""
    # first get first page info in case the object doesn't start with a page tag
    if not config.page_images_url_root:
        return output, {}
    first_page_object = get_first_page(philo_id, config)
    if not first_page_object["filename"]:
        return output, {}
    if not current_obj_img:
        current_obj_img.append('')
    if first_page_object['start_byte'] and current_obj_img[0] != first_page_object['filename'][0]:
        if first_page_object['filename']:
            page_href = config.page_images_url_root + '/' + first_page_object['filename'][0] + config.page_image_extension
            if config.external_page_images is False:
                if len(first_page_object['filename']) == 2:
                    large_img = config.page_images_url_root + '/' + first_page_object['filename'][1] + config.page_image_extension
                else:
                    large_img = config.page_images_url_root + '/' + first_page_object['filename'][0] + config.page_image_extension
                output = '<span class="xml-pb-image"><a href="%s" large-img="%s" class="page-image-link" data-gallery>[page %s]</a></span>' % (page_href, large_img, first_page_object["n"]) + output
                if current_obj_img[0] == '':
                    current_obj_img[0] = first_page_object['filename'][0]
                else:
                    current_obj_img.insert(0, first_page_object['filename'][0])
            else:
                output = '<span class="xml-pb-image"><a href="%s" target="_blank">[page %s]</a></span>' % (page_href, first_page_object["n"]) + output
                return output, {}
        else:
            output = '<span class="xml-pb-image">[page ' + str(first_page_object["n"]) + "]</span>" + output
    ## Fetch all remainging imgs in document
    all_imgs = get_all_page_images(philo_id, config, current_obj_img)
    all_graphics = get_all_graphics(philo_id, config)
    img_obj = {'all_imgs': all_imgs, 'current_obj_img': current_obj_img, "graphics": all_graphics, "current_graphic_img": current_graphic_img}
    return output, img_obj


def get_first_page(philo_id, config):
    """This function will fetch the first page of any given text object in case there's no <pb>
    starting the object"""
    db = DB(config.db_path + '/data/')
    c = db.dbh.cursor()
    if len(philo_id) < 9:
        c.execute('select start_byte, end_byte from toms where philo_id=?', (' '.join([str(i) for i in philo_id]), ))
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
        filename = page_result["facs"]
    except (IndexError, TypeError):
        filename = ""
    if not filename:
        try:
            filename = page_result['id'] or ''
        except (IndexError, TypeError):
            pass
    try:
        n = page_result['n'] or ''
        page = {'filename': filename.split(),
                "n": n,
                'start_byte': page_result['start_byte'],
                'end_byte': page_result['end_byte']}
        return page
    except:  # Let's play it safe
        return {'filename': '', 'start_byte': ''}


def get_all_page_images(philo_id, config, current_obj_imgs):
    """Get all page images"""
    if current_obj_imgs[0]:
        # We know there are images
        db = DB(config.db_path + '/data/')
        c = db.dbh.cursor()
        approx_id = str(philo_id[0]) + ' 0 0 0 0 0 0 %'
        try:
            c.execute('select * from pages where philo_id like ? and facs is not null and facs != ""', (approx_id, ))
            current_obj_imgs = set(current_obj_imgs)
            all_imgs = [tuple(i["facs"].split()) for i in c.fetchall()]
        except sqlite3.OperationalError:
            all_imgs = []
        if not all_imgs:
            try:
                c.execute('select * from pages where philo_id like ? and id is not null and id != ""', (approx_id, ))
                current_obj_imgs = set(current_obj_imgs)
                all_imgs = [tuple(i["id"].split()) for i in c.fetchall()]
            except sqlite3.OperationalError:
                return []
        return all_imgs
    else:
        return []

def get_all_graphics(philo_id, config):
    db = DB(config.db_path + '/data/')
    c = db.dbh.cursor()
    approx_id = str(philo_id[0]) + ' 0 0 0 0 0 0 %'
    try:
        c.execute('SELECT facs FROM graphics WHERE philo_id LIKE ? AND facs IS NOT NULL AND facs != "" ORDER BY ROWID', (approx_id, ))
        graphics = [i["facs"].split() for i in c.fetchall() if i["facs"]]
        return graphics
    except sqlite3.OperationalError:
        return []

def clean_tags(element, word_regex):
    """Remove all tags"""
    text = ''
    for child in element:
        text += clean_tags(child, word_regex)
    if element.tag == "philoHighlight":
        word_match = re.search(word_regex, element.tail)
        if word_match:
            return '<span class="highlight">' + element.text + text + element.tail[:word_match.end(
            )] + "</span>" + element.tail[word_match.end():]
        text = element.text + text + element.tail
        return '<span class="highlight">' + element.text + text + "</span>" + element.tail
    return element.text + text + element.tail
