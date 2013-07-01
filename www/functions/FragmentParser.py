import sys
from lxml import etree
from philologic import shlaxtree as st

class FragmentParser:
    def __init__(self):
        self.root = etree.Element("div",{"class":"philologic-fragment"})
        self.root.text = u""
        self.root.tail = u""
        self.current_el = self.root
        self.current_tail = None

        self.in_tag = True
        self.stack = []

    def start(self,tag,attrib):
        #print >> sys.stderr, "START: " + tag + repr(attrib)
        self.stack.append(tag)
        new_el = etree.SubElement(self.current_el,tag,attrib)
        new_el.text = u""
        new_el.tail = u""
        self.current_el = new_el
        self.in_tag = True
        self.current_tail = None

    def end(self,tag):
        if len(self.stack) and self.stack[-1] == tag:
            #print >> sys.stderr, "END: " + tag
            self.current_tail = self.current_el
            self.stack.pop()            
            self.current_el = self.current_el.getparent()
            self.in_tag = False

        else:
            pass
            #print >> sys.stderr, "UNBALANCED-END: " + tag        

    def data(self,data):
        #print >> sys.stderr, "TEXT: " + data.encode("utf-8")
        if self.current_tail is not None:
            self.current_tail.tail += data
        else:
            self.current_el.text += data

    def comment(self,text):
        pass

    def close(self):
        self.stack.reverse()
        for s in self.stack:
            self.end(s)
        r = self.root
        self.stack = []
        return r

class LXMLTreeDriver:
    def __init__(self,target):
        self.target = target

    def feed(self,*event):
        (kind,content,offset,name,attributes) = event
        #print >> sys.stderr,repr(attributes)
        if kind == "start":
            uni_attrib = {}
            for k,v in attributes.items():
                # hack to handle double quoted empty string values coming up None.  Fixed in rwhaling branch of PhiloLogic4
                if v is None:
                    v = ""
                uni_attrib[k.decode("utf-8","ignore")] = v.decode("utf-8","ignore")
            self.target.start(name,uni_attrib)
        if kind == "end":
            self.target.end(name)
        if kind == "text":
            self.target.data(content.decode("utf-8","ignore"))
    def close(self):
        return self.target.close()

def parse(text):
    parser = FragmentParser()
    driver = LXMLTreeDriver(target=parser)
    feeder = st.ShlaxIngestor(target=driver)
    feeder.feed(text)
    return feeder.close()
    
