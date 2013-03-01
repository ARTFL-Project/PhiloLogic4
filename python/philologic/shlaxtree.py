from philologic import shlax

import re 
import sys

try:
    import lxml.etree as ElementTree
except ImportError:
    try:
        import elementtree.ElementTree as ElementTree
    except ImportError:
        if (sys.version[0] == 2) and (sys.version[1] <= 6):
            print >> sys.stderr, "Warning: PhiloLogic require ElementTree 1.3 or greater"
        import xml.etree.ElementTree as ElementTree
et = ElementTree

def parse(file):
    tokenizer = ShlaxTreeDriver()
    parser = ShlaxIngestor(target=tokenizer)
    for line in file:
        parser.feed(line)
    return parser.close()

def TokenizingParser(start = 0, offsets = None):
    if offsets is None:
        offsets = []
    tokenizer = ShlaxTreeDriver(offsets=offsets)
    parser = ShlaxIngestor(target=tokenizer,byte_offset=start)
    return parser

class ShlaxIngestor():
    def __init__(self,target=None,byte_offset = 0,encoding=None, logfile = None):
        self.target = target or ShlaxTreeDriver(log=logfile)
        self.encoding = encoding
        self.byte_offset = byte_offset
        self.buffer = ""
        self.buffer_offset = byte_offset
        self.closed = False
        self.log = logfile

    def feed(self,data):
#        console.log(data)
        if self.closed:
            return
        self.buffer += data
        last_end = 0
        matches = re.finditer(shlax.pattern,self.buffer,re.DOTALL)
        type = ""
#        matches = list(matches)
#        print >> sys.stderr, repr(matches)

        for m in matches:
            att = {}
            name = ""
            empty = False
            match_start = self.buffer_offset + m.start(0)
            match_end = self.buffer_offset + m.end(0)
            text = self.buffer[last_end:m.start(0)]
            if text:
                type = "text"
                content = text
                offset = self.buffer_offset + last_end
                self.target.feed(type,content,offset,None,None)
            if m.group("EndTag"):
                type = "end"
                content = m.group(0)
                parseable_content = m.group("EndTag")
                offset = match_start
                nm = re.match(shlax.EndTagCE,parseable_content)
                if nm:
                    name = nm.group("EndTagName")   
                else:
                    print "'%s' : no name in end tag?" % content
                self.target.feed(type,content,offset,name,None)
                # have to extract the name, of course.
            elif m.group("ElemTag"):
                type = "start"
                content = m.group(0)
                em = re.match(shlax.ElemTagSPE,content)
                if em.group("Empty"): # very important
                    empty = True
                offset = match_start
                name = em.group("ElemName")
                attributes = em.group("Attributes")
                amatches = re.finditer(shlax.AttributeSPE,attributes)
                for am in amatches: # get the attributes out.  kinda nasty.
                    ad = am.groupdict()
                    aname = am.group("AttName") 
                    aval = ad["DQAttVal"] or ad["SQAttVal"] #single or double quotes...
                    att[aname] = aval
                self.target.feed(type,content,offset,name,att.copy())
            else:
                type = "markup" # comment or processing instruction.  Ignored.
            if empty:
                self.target.feed("end","",offset,name,None)
            last_end = m.end(0)
#            print >> sys.stderr, type + " : " + m.group(0)
        self.buffer_offset = self.buffer_offset + last_end
        self.buffer = self.buffer[last_end:]

    def close(self):
        self.target.feed("text",self.buffer,self.buffer_offset,None,None)
        self.buffer_offset += len(self.buffer)
        self.buffer = ""
        self.closed = True
        return self.target.close()


class ShlaxTreeDriver():
    def __init__(self,target=None, offsets = None,punct_re="\W",wtag="span",watt=None,log=None):
        self.target = target or ShlaxTreeBuilder(log=log)
        if offsets:
            self.offsets = list(offsets)
        else:
            self.offsets = []
        self.punct_re = punct_re
        self.wtag = wtag
        self.watt = watt or {"class":"hilite"}
        self.in_word = False

    def feed(self,*event):
        (kind,content,offset,name,attributes) = event
        start_scan = None
        if kind == "start":
            self.target.start(name,attributes)
        elif kind == "end":
            self.target.end(name)
        elif kind == "text":
            if not self.in_word:
                if self.offsets:
                    next_offset = self.offsets[0]
                    if (offset <= next_offset) and (offset + len(content) > next_offset):
                        breakpoint = next_offset - offset
                        pre_word = content[:breakpoint]
                        rest = content[breakpoint:]
                        self.target.data(pre_word)
                        self.in_word = True
                        self.offsets.pop(0)
                        self.feed("text",rest,offset + breakpoint, None,None)
                    else:
                        self.target.data(content)
                else:
                    self.target.data(content)
            elif self.in_word:
                word_end = re.search(self.punct_re,content) # Modify tokenization function here
                if word_end:

                    breakpoint = word_end.start()
                    word_seg = content[:breakpoint]
                    if len(word_seg) > 0:
                        self.target.start(self.wtag,self.watt)
                        self.target.data(word_seg)
                        self.target.end(self.wtag)
                    self.in_word = False
                    rest = content[breakpoint:]
                    # should check here to make sure we haven't passed two words, I suppose.
                    while self.offsets and offset + len(word_seg) > self.offsets[0]:
                        self.offsets.pop(0)
                    self.feed("text",rest,offset + breakpoint, None,None)
                else:
                    if len(content) == 0:
                        self.target.data(content)
                    else:
                        self.target.start(self.wtag,self.watt)
                        self.target.data(content)                    
                        self.target.end(self.wtag)

    def close(self):
        return self.target.close()


class ShlaxTreeBuilder():
    def __init__(self,element_factory=None, log=None):
        self.element_factory = element_factory
        self.stack = []
        self.done = False
        self.log = log
        
    def close(self):
        if self.stack:
            while self.stack:
                open_element = self.stack.pop()
                if self.log: print >> sys.stderr, "unclosed element %s" % open_element.tag
            return open_element
        else:
            return self.done # return the tree
            
    def data(self,data):
        if self.done is not False:
            return
        if not self.stack:
            return
        current_element = self.stack[-1]
        n_children = len(current_element)
        if n_children == 0:
            try:
                current_element.text += data
            except TypeError:
                current_element.text = data
        else:
            try:
                current_element[n_children - 1].tail += data
            except TypeError:
                current_element[n_children - 1].tail = data

    def start(self,tag,attrs):
        if self.done is not False:
            return
        if len(self.stack) == 0:
            self.stack.append(et.Element(tag,attrs))
        else:
            current_element = self.stack[-1]
            self.stack.append(et.SubElement(current_element,tag,attrs)) 

    def end(self,tag):
        if self.done is not False:
            return
        if not self.stack:
            return
        last_element = self.stack[-1]
        if last_element.tag == tag:
            last_element = self.stack.pop()     
        else:
            if self.log: print >> sys.stderr, "tag mismatch. %s != %s" % (last_element.tag,tag)
        if not self.stack:
           self.done = last_element
        return last_element

if __name__ == "__main__":
    import sys
    for file in sys.argv[1:]:
        root = parse(open(file))
        print "parsed %s successfully." % file
#        print et.tostring(root,encoding="utf8")
