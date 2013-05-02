from lxml import etree
from StringIO import StringIO
import re
import sys

def get_text(obj,words):
    pass

def format(text,words=[]):
#    print >> sys.stderr, "TEXT:",text
    parser = etree.XMLParser(recover=True)
    print >> sys.stderr, "PRE:",text
    xml = etree.parse(StringIO(text.decode("utf-8","ignore")),parser)
    for el in xml.iter():
        print >> sys.stderr, el.tag
        if el.tag == "sc" or el.tag == "scx":
            el.tag = "span"
            el.attrib["class"] = "small-caps"
        elif el.tag == "head":
            el.tag = "b"
            el.append(etree.Element("br"))
        elif el.tag == "pb":
            el.tag = "p"
            el.append(etree.Element("a"))
            el[-1].attrib["href"] = 'http://artflx.uchicago.edu/images/encyclopedie/' + el.attrib["fac"]
            el[-1].text = "[page " + el.attrib["n"] + "]"
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
            el.tag = "span"
            el.attrib["class"] = "highlight"
            word_match = re.match(r"\w+")
            el.text = el.tail[:word_match.end()]
            el.tail = el.tail[word_match.end():]
    return etree.tostring(xml)


    
