from philologic import shlax
import time
import re
import sys

TEIFormat = {"speaker":"\t",
             "/speaker":":\n",
             "head":"\n------\n",
             "/head":"\n------\n",
             "stage":"\n\t\t[",
             "/stage":"]\n",
                         "l":"",
             "/l":"\n",
             "/ab":"\n",
             "p":"\t",
             "/p":"\n",
             "pb":"\n---\n"}

class Formatter:
    def __init__(self, table = TEIFormat):
        self.buffer = ""
        self.table = table
        self.context = []
        self.preserve = None

    def iter_format(self,data):
        self.buffer = ""
        self.context = []
        parser = shlax.parsestring(data)
        for n in parser:
            if n.type == "text":
                self.handle_data(n.content)
                yield self.buffer
                self.buffer = ""
            elif n.type == "StartTag":
                self.handle_starttag(n.name,n.attributes.items())
                yield self.buffer
                self.buffer = ""
            elif n.type == "EndTag":
                self.handle_endtag(n.name)
                yield self.buffer
                self.buffer = ""
        #self.close() 
        #don't close()--croaks on EOF mid-event, which we should assume will happen.
        #instead, we just want to silently discard unparseable data, and close all open tags.
        for tag in self.context:
            if tag in self.table:
                self.buffer += self.table["/" + tag]
                yield self.buffer
                self.buffer = ""                

    def format(self,data):
        self.buffer = ""
        self.context = []
        parser = shlax.parsestring(data)
        for n in parser:
            if n.type == "text":
                self.handle_data(n.content)
            elif n.type == "StartTag":
                self.handle_starttag(n.name,n.attributes.items())
            elif n.type == "EndTag":
                self.handle_endtag(n.name)
        #self.close() 
        #don't close()--croaks on EOF mid-event, which we should assume will happen.
        #instead, we just want to silently discard unparseable data, and close all open tags.
        for tag in self.context:
            if tag in self.table:
                self.buffer += self.table["/" + tag]
        return self.buffer

    def handle_starttag(self,tag,attr):
#        print >> sys.stderr, "start <%s>" % tag
        orig = "<" + tag
        for a in attr:
            orig += " %s='%s'" % (a[0],a[1]) 
        orig += ">"     
        self.context.append(tag)
        if ("rend","preserve") in attr:
            self.preserve = tag
            self.buffer += orig
        else:
            if tag in self.table:
                self.buffer += self.table[tag]

    def handle_endtag(self,tag):
#        print >> sys.stderr, "end <%s>" % tag
        self.preserve = None
#        while len(self.context) != 0 and self.context[-1] != tag:
#            t = self.context.pop()
#            self.handle_endtag(t)
#        if len(self.context) == 0:
#            self.context = [tag] + self.context
#            if tag in self.table:
#                self.buffer = self.table[tag] + self.buffer             
        if self.context:
            self.context.pop()                  
        if "/" + tag in self.table:
            self.buffer += self.table["/" + tag]
    

    def handle_data(self,data):
        data = re.sub("^.*?>","",data,1)
        data = re.sub("\s+"," ",data)
        #data = data.strip() 
        self.buffer += data

