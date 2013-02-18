import philologic.shlax as shlax
import codecs
from philologic.OHCOVector import OHCOVector
import re

#Default configurations.  to be expanded.

ARTFLVector = ["doc","div1","div2","div3","para","sent","word"] # I'd prefer to explicitly nest the divs...

TEIMapping = {# the raw mapping should be unambiguous, and context-free.
                        "front":"div",
                        "div":"div",
                        "div0":"div",
                        "div1":"div",
                        "div2":"div",
                        "div3":"div",
                        "p":"para",
                        "sp":"para",
                        "stage":"para"} # maybe stage directions should go. they mask a lot of <sp>.

TEIPaths = { "doc" : {"titleStmt/author" : "author", # metadata paths; order of evaluation is tricky, so MAKE SURE that they are unambiguous.
                      "titleStmt/title" : "title"},
             "div" : {"head":"head"
#                      "@type":"unit",
#                      "@n":"n"
 					 },
             "para" : {"speaker": "who"}
           }

# a little helper.  move to shlax?

class buffer_stream: # buffers the parse stream so we can push discards back onto it. super useful.
    def __init__(self,stream):
        self.s = iter(stream) # iter() is to stop the stream from getting reset with each for loop.
        self.buffer = []
    
    def __iter__(self):
        for i in self.s:
            for j in self.buffer:
                yield self.buffer.pop()
            yield i
        for j in self.buffer:
            yield j
            
    def append(self,*items):
        for x in items:
            self.buffer.append(x)

class AbstractParser:
    def __init__(self,filename,docid,format=ARTFLVector,mapping=TEIMapping,paths=TEIPaths): 
        self.reader = None
        self.writer = None
        self.filename = filename
        self.object_stack = []
        self.context = []
        self.counts = {}
        self.format = format
        self.objects = OHCOVector(self.format) # the parser should know what its object levels are.
        self.objects.v[0] = docid - 1 # - 1 because we're about to increment it.
        self.full_did = self.objects.v[:]
        self.line_max = 0
        self.mapping = mapping
        self.metapaths = paths
        self.parallel = {"line":0,
                         "byte":0}
        self.event_stream = None
        self.objects_max = None
        
    def parse(self, input, output):
        self.reader = input # filtering for bad encoding should be done in the reader
        self.writer = output # sorting or filtering output should be done by piping the writer
        self.event_stream = buffer_stream(shlax.parser(self.reader))
        for n in self.event_stream:
            if n.type == "StartTag":
                self.make_object(n.name,"doc",n,{"filename":self.filename})
        # note that objects are emitted in the order in which they END, due to the recursion.
        # document finishes last. sort as necessary/desired.
        return (self.objects_max,self.counts)
            
    def make_object(self,name,type, first = None, attributes = {}):
        discard = None
        mydepth = self.objects.typedepth(type)
#        print "pushing %s:%s at depth %d" % (type,name,mydepth)
        self.objects.push(type)
        my_attributes = attributes.copy() # because we don't want the attributes to get modified by inner objects.
        my_attributes["start"] = first.start if first else self.parallel["byte"]

        # here we check if the start tag has any attributes we want to grab.
        for path_type,path,destination in self.get_xpaths():
            (parsed_path,parsed_attr) = parse_xpath(path)
            if path_type != type: continue
            if not parsed_attr: continue
            if context_match(self.context,parsed_path):
                if parsed_attr in first.attributes.keys() and destination not in my_attributes:
                    my_attributes[destination] = first.attributes[parsed_attr]
        
        my_id = self.objects.v[:]
        my_context = self.context[:]
        self.object_stack.append((name,type,my_id,my_context,my_attributes))
        for node in self.event_stream:
            self.parallel["byte"] = node.start

            if node.type == "StartTag":
                self.context.append(node.name)
                if node.name in self.mapping:
                    newtype = self.mapping[node.name]
                    if self.objects.typedepth(newtype) <= mydepth: 
                        #print "bouncing up!"
                        # should set node.attributes["end"] here.
                       discard = node
                       break
#                        pass
                    # should check here whether new type is child of this type, or else set discard and break. 
                    inner_result = self.make_object(node.name,newtype,node,{"parent":" ".join(str(i) for i in my_id)})
                    if inner_result:
                        self.event_stream.append(inner_result) # result gets pushed onto the front of the loop.
                elif node.name == "l": #parallel objects are best handled with one-off hacks, for now.  maybe a "dispatch" keyword in the mapping?
                    if "n" in node.attributes.keys():
                        self.parallel["line"] = int(node.attributes["n"])
                    else:
                        self.parallel["line"] += 1
                #   self.emit("line", node.name,self.full_did,self.parallel["byte"],self.parallel["line"]) # need to work out a notation for parallel objects.
                    self.line_max = max(self.parallel["line"],self.line_max)
                else:
                    pass # dispatch child attributes here.

            elif node.type == "text":
                self.tokenize(node.content,node.start)

            elif node.type == "EndTag":
                if len(self.context) and self.context[-1] == node.name: # very conservative--this makes the stack tend to grow.
                    self.context.pop()
                if node.name == name: # we know this is the end because self.mapping is unambiguous, right?
                    my_attributes["end"] = node.start + len(node.content)
                    break
        if "end" not in my_attributes:
            my_attributes["end"] = self.parallel["byte"]
        self.emit(type,name, my_id,my_attributes["start"],self.parallel["line"],**my_attributes)
        self.object_stack.pop()
        self.objects.pull(type)
        return discard

    def tokenize(self,text,offset):
        try: # long try blocks are bad, they say...so is python's utf-8 handling.
            text = text.decode("utf-8")
            tokens = re.finditer(ur"([\w\u2019]+)|([\.;:?!])",text,re.U)
            # todo: name regex subgroups.

            for path_type,path,destination in self.get_xpaths():
                (parsed_path,parsed_attr) = parse_xpath(path)
                if parsed_attr: continue
                parent_match = self.match_parents(parsed_path,path_type)
                if parent_match:
                    parent_match[4][destination] = parent_match[4].get(destination,"") + re.sub("[\n\t]","",text.encode("utf-8"))
                    break
            if parent_match: pass # don't tokenize if you are in metadata

            else:
                for token in tokens:
                    if token.group(1):
                        self.objects.push("word")
                        char_offset = token.start(1)
                        byte_length = len(text[:char_offset].encode("utf-8"))
                        self.emit("word",token.group(1),self.objects.v,offset + byte_length,self.parallel["line"]) 
                        self.counts[token.group(1)] = self.counts.get(token.group(1),0) + 1
                    if token.group(2):
                        self.objects.push("sent")
                        char_offset = token.start(2)
                        byte_length = len(text[:char_offset].encode("utf-8"))
                        self.emit("sent",token.group(2),self.objects.v,offset + byte_length,self.parallel["line"]) 

        except UnicodeDecodeError as err:
            print >> sys.stderr, "%s : %s@%s : %s;%s" % (type(err),self.filename,offset,err,err.args)

    def emit(self,type,name,vector,*parallel,**attr):
        v = vector[:]
        if parallel:
            v += parallel
        if attr:
            v.append(attr)
        print >> self.writer, "%s\t%s\t%s" % (type,name," ".join(str(x) for x in v) )     
        try: 
            self.objects_max = [max(x,y) for x,y in zip(v,self.objects_max)]
        except TypeError:
            self.objects_max = v

    def match_parents(self,parsed_path,path_type=None):
        for parent in reversed(self.object_stack):
            (parent_name,parent_type,parent_id,parent_context,parent_attributes) = parent
            if self.context[:len(parent_context)] != parent_context: continue
            if parent_type not in self.metapaths: continue 
            if path_type: 
                if parent_type != path_type: continue
            working_context = self.context[len(parent_context):] 
            if context_match(working_context,parsed_path):
                return parent
            
    def get_xpaths(self):
        return [(this_type,this_path,this_destination) for this_type in self.metapaths for (this_path,this_destination) in self.metapaths[this_type].items()]

def context_match(context,parsed_pattern): # should be modified to simply IGNORE @attributes
    nodes = parsed_pattern
    for node in nodes:
        if node in context:
            position = context.index(node)
            context = context[position:]
        else:
            return False
    return True

def parse_xpath(pattern): # should return any trailing @attribute leaf node from a path.
    nodes = [x for x in pattern.split("/") if x != ""]
    if len(nodes):
        if nodes[-1][0] == "@":
            return (nodes[:-1],nodes[-1][1:])

    return (nodes,None)

if __name__ == "__main__":
    import sys
    did = 1
    files = sys.argv[1:]
    for docid, filename in enumerate(files):
        f = open(filename)
        o = codecs.getwriter('UTF-8')(sys.stdout)
        p = AbstractParser(filename,docid + did)
        spec,counts = p.parse(f,o)
        print >> sys.stderr, "%s\n%d total tokens in %d unique types." % (spec,sum(counts.values()),len(counts.keys()))
