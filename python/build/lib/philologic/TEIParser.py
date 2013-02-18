#!/usr/bib/env python
from OHCOVector import *
import xml.parsers.expat
import re


class TEIParser:
    def __init__(self, filename, docid):
        self.reader = None
        self.writer = None
        self.filename = filename
        
        self.context = []
        self.metahandler = None
        self.objects = OHCOVector(["doc","div1","div2","div3","para","sent","word"])
        self.objects.v[0] = docid
        
        self.mapping = {"TEI":"doc",
                        "front":"div",
                        "div":"div",
                        "div0":"div",
                        "div1":"div",
                        "div2":"div",
                        "div3":"div",
                        "p":"para",
                        "sp":"para",
                        "stage":"para"}

        self.metamap = { "titleStmt/author" : "author",
                         "titleStmt/title" : "title",
                         "div/head" : "head"}

        self.parallel = {"line":0,
                         "byte":0}

        self.parser = xml.parsers.expat.ParserCreate()
        self.parser.StartElementHandler = self.tagstart
        self.parser.EndElementHandler = self.tagend
        self.parser.CharacterDataHandler = self.tokenizer

    def parse(self, input,output):
        self.reader = input
        self.writer = output
        self.parser.ParseFile(self.reader)
        
    def context_match(self,context,pattern):
        nodes = [x for x in pattern.split("/") if x != ""]
        for node in nodes:
            if node in context:
                position = context.index(node)
                context = context[position:]
            else:
                return False
        return True
        
    #next, we start to build up the handlers that will accept expat events.
    def tagstart(self,name,attributes):
        """translates xml tags into OHCOVector push events 
           by looking them up in a mapping"""
        self.parallel["byte"] = self.parser.CurrentByteIndex
        self.context.append(name)
        for pattern in self.metamap:
            if self.context_match(self.context,pattern):
                self.metahandler = self.metamap[pattern]
        if name in self.mapping:
            type = self.mapping[name]
            self.objects.push(type)
            attlist = ""
            for k,v in attributes.iteritems():
                attlist += " %s=\"%s\"" % (k,v) 
            print >> self.writer, type + " " + "<" + name + attlist + "> " + \
                  " ".join(map(str,self.objects.v)) + " " + str(self.parallel["byte"]) + \
                  " " + str(self.parallel["line"])
            if type == "doc":
                print >> self.writer, "meta %s %s" % ("filename", self.filename)
        if name == "l":
            if "n" in attributes.keys():
                self.parallel["line"] = int(attributes["n"])
            else:
                self.parallel["line"] += 1
            print >> self.writer, "line %d %d" % (self.parallel["byte"],self.parallel["line"])
        
    def tagend(self,name):
        """translates xml end tags into OHCOVector pull events"""
        self.parallel["byte"] = self.parser.CurrentByteIndex
        for pattern in self.metamap:
            if self.context_match(self.context,pattern):
                self.metahandler = None
        self.context.pop()
        if name in self.mapping:
            type = self.mapping[name]
            #print "found %s, pulling from %s" % (name, type)
            self.objects.pull(type)
            print >> self.writer, type + " " + "</" + name + ">" + " ".join(map(str,self.objects.v)) + \
                   " " + str(self.parallel["byte"]) + " " + str(self.parallel["line"])
            
    def tokenizer(self,text):
        """uses a regex to split text into sentences and words, 
           and pushes each into the OHCOVector.  A more sophisticated implementation 
           would have a buffer, and check for tag-spanning words, or if we're in a 
           metadata tag, and dispatch tokens accordingly."""
        self.parallel["byte"] = self.parser.CurrentByteIndex
        tokens = re.finditer(ur"([\w\u2019]+)|([\.;:?!])",text,re.U)
        offset = self.parallel["byte"]
        if self.metahandler:
            cleantext = re.sub("[\n\t]"," ",text)
            print >> self.writer, "meta %s %s" % (self.metahandler,cleantext)
        for token in tokens:
            if token.group(1):
                self.objects.push("word")
                char_offset = token.start(1)
                byte_length = len(text[:char_offset].encode("UTF-8"))
                print >> self.writer, "word " + token.group(1) + " " + " ".join(map(str,self.objects.v)) \
                      + " " + str(offset + byte_length) + " " + str(self.parallel["line"])
            if token.group(2):
                self.objects.push("sent")
                char_offset = token.start(1)
                byte_length = len(text[:char_offset].encode("UTF-8"))
                print >> self.writer, "sent " + token.group(2) + " " + " ".join(map(str,self.objects.v)) \
                       + " " + str(offset + byte_length) + " " + str(self.parallel["line"])

