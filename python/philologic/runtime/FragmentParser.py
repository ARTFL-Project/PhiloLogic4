#!/usr/bin/env python3


import re

from lxml import etree
from philologic import shlaxtree as st


class FragmentParser:
    """Fragment Parser: reconstructs broken trees"""

    def __init__(self):
        self.root = etree.Element("div", {"class": "philologic-fragment"})
        self.root.text = ""
        self.root.tail = ""
        self.current_el = self.root
        self.current_tail = None
        self.in_tag = True
        self.stack = []

    def start(self, tag, attrib):
        # print >> sys.stderr, "START: " + tag + repr(attrib)
        self.stack.append(tag)
        for k, v in list(attrib.items()):
            no_ns_k = re.sub(r"^.*?:", "", k)
            if no_ns_k != k:
                del attrib[k]
                attrib[no_ns_k] = v
        new_el = etree.SubElement(self.current_el, tag, attrib)
        new_el.text = ""
        new_el.tail = ""
        self.current_el = new_el
        self.in_tag = True
        self.current_tail = None

    def end(self, tag):
        if len(self.stack) and self.stack[-1] == tag:
            # print >> sys.stderr, "END: " + tag
            self.current_tail = self.current_el
            self.stack.pop()
            self.current_el = self.current_el.getparent()
            self.in_tag = False

        else:
            pass

    def data(self, data):
        if self.current_tail is not None:
            self.current_tail.tail += data
        else:
            self.current_el.text += data

    def comment(self, text):
        pass

    def close(self):
        self.stack.reverse()
        for s in self.stack:
            self.end(s)
        r = self.root
        self.stack = []
        return r


class LXMLTreeDriver:
    def __init__(self, target):
        self.target = target

    def feed(self, *event):
        (kind, content, offset, name, attributes) = event
        if kind == "start":
            uni_attrib = {}
            for k, v in list(attributes.items()):
                # hack to handle double quoted empty string values coming up None.  Fixed in rwhaling branch of PhiloLogic4
                if v is None:
                    v = ""
                uni_attrib[k] = v
            self.target.start(name, uni_attrib)
        if kind == "end":
            self.target.end(name)
        if kind == "text":
            self.target.data(content)

    def close(self):
        return self.target.close()


class FragmentStripper:
    def __init__(self):
        self.buffer = ""

    def feed(self, *event):
        (kind, content, offset, name, attributes) = event
        if kind == "text":
            self.buffer += content

    def close(self):
        return self.buffer


def parse(text):
    try:
        parser = FragmentParser()
        driver = LXMLTreeDriver(target=parser)
        feeder = st.ShlaxIngestor(target=driver)
        feeder.feed(text)
        return feeder.close()
    except ValueError:
        # we use LXML's HTML parser which is more flexible and then feed the result to fragment parser
        parser = etree.HTMLParser()
        tree = etree.fromstring(text, parser=parser)
        new_text = (
            etree.tostring(tree, method="xml")
            .replace("<html><body>", "")
            .replace("</body></html>", "")
            .replace("philohighlight", "philoHighlight")
        )
        parser = FragmentParser()
        driver = LXMLTreeDriver(target=parser)
        feeder = st.ShlaxIngestor(target=driver)
        feeder.feed(new_text)
        return feeder.close()


def strip_tags(text):
    parser = FragmentStripper()
    feeder = st.ShlaxIngestor(target=parser)
    feeder.feed(text)
    return feeder.close()
