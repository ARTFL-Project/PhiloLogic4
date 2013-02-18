from philologic.OHCOVector import *
import philologic.shlax as shlax
import re
import os
import philologic.Toms as Toms

class AbstractParser:
    def __init__(self,filename,docid): # should take object levels, mapping, metapaths as keyword arguments.
        self.reader = None
        self.writer = None
        self.filename = filename
        self.context = []
        self.counts = {}
        self.current_object = {}
        self.meta_memory = {}
        self.metahandler = None
        self.objects = OHCOVector(["doc","div1","div2","div3","para","sent","word"]) # the parser should know what its object levels are.
        self.objects.v[0] = docid - 1 # - 1 because we're about to increment it.
        self.objects_max = self.objects.v
        self.line_max = 0
        self.mapping = {"TEI":"doc",  # the raw mapping should be unambiguous, and context-free.
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
                        # we should be able to put bonus items in here.  "ln":"line", in particular.
        self.metamap = { "titleStmt/author" : "author", 
                         "titleStmt/title" : "title",
                         "div/head" : "head",
                         "div1/head" : "head"}
        self.metapaths = { "doc" : {"titleStmt/author" : "author", # metadata paths; order of evaluation is indeterminate, so MAKE SURE that they are unambiguous.
                                    "titleStmt/title" : "title"},
                           "div" : {"head":"head"}
                         } # attributes should go in here too.
        self.context_memory = {}
        self.parallel = {"line":0, #this should be implicit.
                         "byte":0} # this should be automatic.

    def parse_metapaths(self):
        pass
        
    def match_metapaths(self):
        for obj_type, paths in self.metapaths.items():
            if obj_type in self.meta_memory and self.meta_memory[obj_type]:
                working_context = self.context[len(self.meta_memory[obj_type]):]
#                print self.context
#                print working_context
#                print self.current_object[obj_type]
                #metadata xpaths are ALWAYS relative.  I should check for that.
                for path, destination in paths.items():
                    if context_match(working_context,path):
                        leaf = attribute_leaf(path)
                        if leaf:
                            return ("meta_attribute",obj_type,leaf)
                        else:
                            return ("meta_content",obj_type,destination)
        
    def push_object(self,type):
        self.objects.push(type)
        self.current_object[type] = self.objects.v[:]
        self.meta_memory[type] = self.context[:]
        self.objects_max = [max(x,y) for x,y in zip(self.objects.v,self.objects_max)]
        #should maintain a toms stack here, basically.

    def pull_object(self,type):
        self.objects.pull(type)
        self.current_object[type] = None
        self.meta_memory[type] = None
        self.objects_max = [max(x,y) for x,y in zip(self.objects.v,self.objects_max)]
        #should remove toms from the stack and print them here.

    def parse(self, input, output):
        self.reader = input
        self.writer = output
        p = shlax.parser(self.reader)
        for n in p:
            if n.type == "StartTag":
                self.parallel["byte"] = n.start
                self.context.append(n.name)
                #match metadata after you append: you want to see if you're entering a metadata context.
                for pattern in self.metamap:
                    if context_match(self.context,pattern):
                        self.metahandler = self.metamap[pattern]
                        self.context_memory = self.context
#                meta_result = self.match_metapaths()
#                if meta_result: print meta_result
                if n.name in self.mapping:
                    type = self.mapping[n.name]
                    self.push_object(type)
                    attlist = ""
                    for k,v in n.attributes.items():
                        attlist += " %s=\"%s\"" % (k,v)
                    try:
                        emit_object(self.writer,type,"<" + n.name + attlist + ">",self.objects.v,self.parallel["byte"],self.parallel["line"])
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
                    self.line_max = max(self.parallel["line"],self.line_max)
            elif n.type == "EndTag":
                self.parallel["byte"] = n.start
                #match metadata before you pop: you want to see if you're leaving a metadata context.
                for pattern in self.metamap:
                    if self.context_memory and self.context_memory == self.context:
                        self.metahandler = None
                        self.context_memory = None
                if self.context[-1] == n.name:
                    self.context.pop()
                else:
                    print >> sys.stderr, "mismatched tag at %s byte %s" % (self.filename,n.start)
                if n.name in self.mapping:
                    type = self.mapping[n.name]
                    self.pull_object(type)
                    emit_object(self.writer,type,"</" + n.name + ">",self.objects.v,self.parallel["byte"],self.parallel["line"])                           
            elif n.type == "text":
                self.parallel["byte"] = n.start 
                try: # this tokenizer could go into it's own subroutine...
                    text = n.content.decode("UTF-8")
                    tokens = re.finditer(ur"([\w\u2019]+)|([\.;:?!])",text,re.U)
                    offset = self.parallel["byte"]
                    if self.metahandler:
                        cleantext = re.sub("[\n\t]"," ",text)
                        print >> self.writer, "meta %s %s" % (self.metahandler,cleantext)
                    for token in tokens:
                        if token.group(1):
                            self.push_object("word")
                            char_offset = token.start(1)
                            byte_length = len(text[:char_offset].encode("UTF-8"))
                            emit_object(self.writer,"word",token.group(1),self.objects.v,offset + byte_length,self.parallel["line"])                           
                            self.counts[token.group(1)] = self.counts.get(token.group(1),0) + 1
                        if token.group(2):
                            self.push_object("sent")
                            char_offset = token.start(1)
                            byte_length = len(text[:char_offset].encode("UTF-8"))
                            emit_object(self.writer,"sent",token.group(2),self.objects.v,offset + byte_length,self.parallel["line"])                           
                except UnicodeDecodeError:
                    print >> sys.stderr, "bad encoding in %s around byte %s" % (self.filename,n.start)
        #Here [after done parsing] I should see if I still have an object stack, and unwind it, if so.
        max_v = self.objects_max
        max_v.extend((self.parallel["byte"],self.line_max))
        return (max_v,self.counts)

#And a few helper functions.
def emit_object(destination, type, content, vector, *bonus):
    print >> destination, "%s %s %s %s" % (type,
                                           content,
                                           " ".join(str(x) for x in vector),
                                           " ".join(str(x) for x in bonus)
                                          )

def context_match(context,pattern): # should be modified to simply IGNORE @attributes
    nodes = [x for x in pattern.split("/") if x != ""]
    for node in nodes:
        if node in context:
            position = context.index(node)
            context = context[position:]
        else:
            return False
    return True

def attribute_leaf(pattern): # should return any trailing @attribute leaf node from a path.
    return None

if __name__ == "__main__":
    import sys
    did = 1
    files = sys.argv[1:]
    for docid, filename in enumerate(files):
        f = open(filename)
        o = codecs.getwriter('UTF-8')(sys.stdout)
        p = AbstractParser(filename,docid)
        spec,counts = p.parse(f,o)
        print "%s\n%d total tokens in %d unique types." % (spec,sum(counts.values()),len(counts.keys()))
