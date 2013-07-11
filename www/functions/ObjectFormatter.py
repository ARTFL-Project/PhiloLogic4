from lxml import etree
from StringIO import StringIO
import FragmentParser
import re
import sys
import htmlentitydefs

def get_text(obj,words):
    pass

def adjust_bytes(bytes, length):
    """Readjust byte offsets for concordance"""
    ### Called from every report that fetches text and needs highlighting
    bytes = sorted(bytes) # bytes aren't stored in order
    byte_start = bytes[0] - (length / 2)
    first_hit =  length / 2
    if byte_start < 0:
        first_hit = first_hit + byte_start ## this is a subtraction really
        byte_start = 0
    new_bytes = []
    for pos, word_byte in enumerate(bytes):
        if pos == 0:
            new_bytes.append(first_hit)
        else:
            new_bytes.append(word_byte - byte_start)
    return new_bytes, byte_start

def format(text,bytes=[]):
#    print >> sys.stderr, "TEXT:",text
    parser = etree.XMLParser(recover=True)
    if bytes:
        new_text = ""
        last_offset = 0
        for b in bytes:
            new_text += text[last_offset:b] + "<philoHighlight/>"
            last_offset = b
        text = new_text + text[last_offset:]
    text = "<div>" + text + "</div>"
    xml = FragmentParser.parse(text)
    print >> sys.stderr, "RAW_XML",etree.tostring(xml)
    for el in xml.iter():        
        try:
            if el.tag == "sc" or el.tag == "scx":
                el.tag = "span"
                el.attrib["class"] = "small-caps"
            elif el.tag == "head":
                el.tag = "b"
                el.attrib["class"] = "headword"
                el.append(etree.Element("br"))
            elif el.tag == "pb" and "fac" in el.attrib and "n" in el.attrib:
                el.tag = "p"
                el.append(etree.Element("a"))
                el[-1].attrib["href"] = 'http://artflx.uchicago.edu/images/encyclopedie/' + el.attrib["fac"]
                el[-1].text = "[page " + el.attrib["n"] + "]"
                el[-1].attrib['class'] = "page_image_link"
            elif el.tag == "figure":
                if el[0].tag == "graphic":
                    img_url = el[0].attrib["url"].replace(":","_")
                    volume = re.match("\d+",img_url).group()
                    url_prefix = "http://artflx.uchicago.edu/images/encyclopedie/V" + volume + "/plate_"
                    el.tag = "a"
                    el.attrib["href"] = url_prefix + img_url + ".jpeg"
                    el[0].tag = "img"
                    el[0].attrib["src"] = url_prefix + img_url + ".sm.jpeg"
                    del el[0].attrib["url"]
                    el.append(etree.Element("br"))
            elif el.tag == "philoHighlight":        
                word_match = re.match(r"\w+", el.tail, re.U)
                el.text = el.tail[:word_match.end()]
                el.tail = el.tail[word_match.end():]
                el.tag = "span"
                el.attrib["class"] = "highlight"
        except:
            pass
    output = etree.tostring(xml)
    ## remove spaces around hyphens and apostrophes
    output = re.sub(r" ?([-'])+ ", '\\1', output)
    return convert_entities(output.decode('utf-8', 'ignore')).encode('utf-8')


def format_concordance(text,bytes=[]):
    removed_from_start = 0
    begin = re.search('^[^<]*?>', text)
    if begin:
        removed_from_start = len(begin.group(0))
        text = text[begin.end(0):]
    removed_from_end = 0
    end = re.search('<[^>]*?$', text)
    if end:
        removed_from_end = len(end.group(0))
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
    length = 0
    for el in xml.iter():
        if el.tag == "sc" or el.tag == "scx":
            el.tag = "span"
            el.attrib["class"] = "small-caps"
        elif el.tag == "head":
            el.tag = "span"
        elif el.tag == "pb":
            el.tag = 'span'
        elif el.tag == 'p':
            el.tag ="span"
        elif el.tag == "philoHighlight":        
            word_match = re.match(r"\w+", el.tail, re.U)
            if word_match:
                el.text = el.tail[:word_match.end()]
                el.tail = el.tail[word_match.end():]
            el.tag = "span"
            el.attrib["class"] = "highlight"
    
    output = etree.tostring(xml)
    output = re.sub(r'\A<div class="philologic-fragment">', '', output)
    output = re.sub(r'</div>\Z', '', output)
    return output


def format_strip(text,bytes=[], chars=40):
    removed_from_start = 0
    begin = re.search(r'^[^<]*?>', text)
    if begin:
        removed_from_start = len(begin.group(0))
        text = text[begin.end(0):]
    start_cutoff = re.search(r'^[^ <]+', text)
    if start_cutoff:
        removed_from_start += len(start_cutoff.group(0))
        text = text[start_cutoff.end(0):]
    removed_from_end = 0
    end = re.search(r'<[^>]*?\Z', text)
    if end:
        removed_from_end = len(end.group(0))
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
    return clean_tags(xml)

def clean_tags(element):
    text = u''
    for child in element:
        text += clean_tags(child)
    if element.tag == "philoHighlight":
        word_match = re.match(r"\w+", element.tail, re.U)
        if word_match:
            return '<span class="highlight">' + element.text + text + element.tail[:word_match.end()] + "</span>" + element.tail[word_match.end():]
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
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)
