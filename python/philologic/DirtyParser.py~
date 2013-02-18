from OHCOVector import *
import shlax
import re
import os
import Toms

def parsework(info):
	sortkeys = "-k 1,1 -k 2,2n -k 3,3n -k 4,4n -k 5,5n -k 6,6n -k 7,7n -k 8,8n"
	(docid,path,textdir,workdir) = info
	f = open(path)
	filename = os.path.basename(path)
	origpath = os.path.abspath(path)
	newpath = textdir + filename
	os.system("cp %s %s" % (origpath, newpath))
	outpath = workdir + filename + ".raw"
	o = codecs.open(outpath, "w", "utf-8")
	print "parsing %d : %s" % (docid,filename)
	parser = DirtyParser(filename,docid)
	parser.parse(f,o)
	wordcommand = "cat %s | egrep \"^word \" | cut -d \" \" -f 2,3,4,5,6,7,8,9,10,11 | sort %s > %s" % (outpath,sortkeys,workdir + filename + ".words.sorted")
	os.system(wordcommand)
	tomsfile = workdir + filename + ".toms"
	Toms.mktoms(open(outpath),open(tomsfile,"w"))
	sortedtomsfile = workdir + filename + ".toms.sorted"
	os.system("cat %s | sort -k 1,1n -k 2,2n -k 3,3n -k 4,4n -k 5,5n > %s" % (tomsfile,sortedtomsfile))

class DirtyParser:
    def __init__(self,filename,docid):
        self.reader = None
        self.writer = None
        self.filename = filename
        self.context = []
        self.metahandler = None
        self.objects = OHCOVector(["doc","div1","div2","div3","para","sent","word"])
        self.objects.v[0] = docid
        
        self.mapping = {"TEI":"doc",
                        "TEI.2":"doc",
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
                         "div/head" : "head",
                         "div1/head" : "head"}
        self.context_memory = None
        self.parallel = {"line":0,
                         "byte":0}

    def context_match(self,context,pattern):
        nodes = [x for x in pattern.split("/") if x != ""]
        for node in nodes:
            if node in context:
                position = context.index(node)
                context = context[position:]
            else:
                return False
        return True

    def parse(self, input, output):
        self.reader = input
        self.writer = output
        p = shlax.parser(self.reader)
        for n in p:
            if n.type == "StartTag":
                self.parallel["byte"] = n.start
                self.context.append(n.name)
                for pattern in self.metamap:
                    if self.context_match(self.context,pattern):
                        self.metahandler = self.metamap[pattern]
                        self.context_memory = self.context
                if n.name in self.mapping:
                    type = self.mapping[n.name]
                    self.objects.push(type)
                    attlist = ""
                    for k,v in n.attributes.items():
                        attlist += " %s=\"%s\"" % (k,v)
                    try:
                        print >> self.writer, type + " " + "<" + n.name + attlist + "> " + \
                            " ".join(map(str,self.objects.v)) + " " + str(self.parallel["byte"]) + \
                            " " + str(self.parallel["line"])
                    except UnicodeDecodeError:
                        print >> sys.stderr, "bad encoding at %s byte %s" % (self.filename,n.start)
                    if type == "doc":
                        print >> self.writer, "meta %s %s" % ("filename", self.filename)
                if n.name == "l":
                    if "n" in n.attributes.keys():
                        self.parallel["line"] = int(n.attributes["n"])
                    else:
                        self.parallel["line"] += 1
                    print >> self.writer, "line %d %d" % (self.parallel["byte"],self.parallel["line"])
            elif n.type == "EndTag":
                self.parallel["byte"] = n.start         
                for pattern in self.metamap:
                    if self.context_memory and self.context_memory == self.context:
                        self.metahandler = None
                        self.context_memory = None
                try:
                    self.context.pop()
                except IndexError:
                    print >> sys.stderr, "mismatched tag at %s byte %s" % (self.filename,n.start)
                if n.name in self.mapping:
                    type = self.mapping[n.name]
                    self.objects.pull(type)
                    print >> self.writer, type + " " + "</" + n.name + ">" + " ".join(map(str,self.objects.v)) + \
                        " " + str(self.parallel["byte"]) + " " + str(self.parallel["line"])
            elif n.type == "text":
                self.parallel["byte"] = n.start
                try:
                    text = n.content.decode("UTF-8")
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
                except UnicodeDecodeError:
                    print >> sys.stderr, "bad encoding in %s around byte %s" % (self.filename,n.start)
        
if __name__ == "__main__":
    import sys
    did = 1
    files = sys.argv[1:]
    for docid, filename in enumerate(files):
        f = open(filename)
        o = codecs.getwriter('UTF-8')(sys.stdout)
        p = DirtyParser(filename,docid)
        p.parse(f,o)