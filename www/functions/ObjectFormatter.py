#!/usr/bin/env python
import FragmentParser
import re
import htmlentitydefs

begin_match = re.compile(r'^[^<]*?>')
start_cutoff_match = re.compile(r'^[^ <]+')
end_match = re.compile(r'<[^>]*?\Z')
space_match = re.compile(r" ?([-'])+ ")
term_match = re.compile(r"\w+", re.U)

entities_match = re.compile("&#?\w+;")

# Source: https://developer.mozilla.org/en-US/docs/Web/Guide/HTML/HTML5/HTML5_element_list
valid_html_tags = set(
    ['html', 'head', 'title', 'base', 'link', 'meta', 'style', 'script',
     'noscript', 'template', 'body', 'section', 'nav', 'article', 'aside',
     'h1', ',h2', ',h3', ',h4', ',h5', ',h6', 'header', 'footer', 'address',
     'main', 'p', 'hr', 'pre', 'blockquote', 'ol', 'ul', 'li', 'dl', 'dt',
     'dd', 'figure', 'figcaption', 'div', 'a', 'em', 'strong', 'small', 's',
     'cite', 'q', 'dfn', 'abbr', 'data', 'time', 'code', 'var', 'samp', 'kbd',
     'sub', 'sup', 'i', 'b', 'u', 'mark', 'ruby', 'rt', 'rp', 'bdi', 'bdo',
     'span', 'br', 'wbr', 'ins', 'del', 'img', 'iframe', 'embed', 'object',
     'param', 'video', 'audio', 'source', 'track', 'canvas', 'map', 'area',
     'svg', 'math', 'table', 'caption', 'colgroup', 'col', 'tbody', 'thead',
     'tfoot', 'tr', 'td', 'th', 'form', 'fieldset', 'legend', 'label', 'input',
     'button', 'select', 'datalist', 'optgroup', 'option', 'textarea',
     'keygen', 'output', 'progress', 'meter', 'details', 'summary', 'menuitem',
     'menu'])


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
    byte_start = bytes[0] - padding
    first_hit = bytes[0] - byte_start
    if byte_start < 0:
        first_hit = first_hit + byte_start  ## this is a subtraction really
        byte_start = 0
    new_bytes = []
    for pos, word_byte in enumerate(bytes):
        if pos == 0:
            new_bytes.append(first_hit)
        else:
            new_bytes.append(word_byte - byte_start)
    return new_bytes, byte_start


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


def clean_tags(element):
    text = u''
    for child in element:
        text += clean_tags(child)
    if element.tag == "philoHighlight":
        word_match = term_match.match(element.tail)
        if word_match:
            return '<span class="highlight">' + element.text + text + element.tail[:word_match.end(
            )] + "</span>" + element.tail[word_match.end():]
        text = element.text + text + element.tail
        return '<span class="highlight">' + element.text + text + "</span>" + element.tail
    return element.text + text + element.tail


def convert_entities(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text  # leave as is

    return entities_match.sub(fixup, text)
