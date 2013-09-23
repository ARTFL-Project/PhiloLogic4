from philologic import OHCOVector, shlaxtree
from philologic.ParserHelpers import *
import re
import sys
from lxml import etree
from xml.parsers import expat
et = etree  # MAKE SURE you use ElementTree version 1.3.
                   # This is standard in Python 2.7, but an add on in 2.6,


# A list of valid types in the Philo object hierarchy, used to construct an OHCOVector.Stack
# The index is constructed by "push" and "pull" operations to various types, and sending metadata into them.
# Don't try to push or pull byte objects.  we populate it by hand right now.
# Keep your push and pulls matched and nested unless you know exactly what you're doing.

ARTFLVector = ["doc","div1","div2","div3","para","sent","word"]
ARTFLParallels = "page"

# The compressor is NOT configurable in this version, so DON'T change this format.
# Feel free to re-purpose the "page" object to store something else: line numbers, for example.

# The Element -> OHCOVector.Record mapping should be unambiguous, and context-free. 
# They're evaluated relative to the document root--note that if the root is closed and discarded, you're in trouble.
# TODO: add xpath support soon, for attribute matching. <milestone unit='x'>, for example.

TEI_XPaths = {  ".":"doc", # Always fire a doc against the document root.
                ".//front":"div",
                ".//div":"div",
                ".//div0":"div",
                ".//div1":"div",
                ".//div2":"div",
                ".//div3":"div",
#                ".//p":"para",
#                ".//sp":"para",
                #"stage":"para"
                ".//pb":"page",
             } 

# Relative xpaths for metadata extraction.  look at the constructors in TEIHelpers.py for details.
# Make sure they are unambiguous, relative to the parent object.
# Note that we supply the class and its configuration arguments, but don't construct them yet.
# Full construction is carried out when new records are created, supplying the context and destination.

TEI_MetadataXPaths = { "doc" : [(ContentExtractor,"./teiHeader/fileDesc/titleStmt/author","author"),
                      (ContentExtractor,"./teiHeader/fileDesc/titleStmt/title", "title"),
                      (ContentExtractor,"./teiHeader/profileDesc/creation/date", "date"),                      
                      (AttributeExtractor,".@xml:id","id")],
             "div" : [(ContentExtractor,"./head","head"),
                      (AttributeExtractor,".@n","n"),
                      (AttributeExtractor,".@xml:id","id")],
             "para": [(ContentExtractor,"./speaker", "who")],
             "page": [(AttributeExtractor,".@n","n"),
                      (AttributeExtractor,".@src","img")],
           }

Default_Token_Regex = r"([\w]+)|([\.;:?!])"

class ExpatWrapper:
    
    def start_element(self,name, attrs):
        print >> sys.stderr, name,attrs
        buffer = self.p.GetInputContext()
        tag_end = buffer.index(">")        
        content = buffer[:tag_end]
#        utf8_attrs = {}
#        for k,v in attrs.items():
#            utf8_attrs[k] = v.encode("utf-8")
        self.target.feed("start",content,self.p.CurrentByteIndex,name,attrs.copy())
    def end_element(self,name):
        closer = (u"</%s>" % name)
        closer_len = len(closer)
        buffer = self.p.GetInputContext()
#        print >> sys.stderr, repr(buffer)
        if buffer[:closer_len] == closer.encode("utf-8"):
            content_length = closer_len
        else:
            content_length = 0
        content = buffer[:content_length]
        self.target.feed("end",content,self.p.CurrentByteIndex,name,None)
    def char_data(self,data):
        data_len = len(data.encode("utf-8"))
        self.target.feed("text",data,self.p.CurrentByteIndex,None,None)
    def __init__(self,target):
        self.target = target
        self.p = expat.ParserCreate(namespace_separator=" ")    
        self.p.StartElementHandler = self.start_element
        self.p.EndElementHandler = self.end_element
        self.p.CharacterDataHandler = self.char_data
    def parse(self,file):      
        self.p.ParseFile(file)        
        return self.target.close()

class StrictParser:
    def __init__(self,output,docid,types=ARTFLVector,parallel=ARTFLParallels,xpaths=None,metadata_xpaths = None,token_regex=Default_Token_Regex,non_nesting_tags = [],self_closing_tags = [],pseudo_empty_tags = [],**known_metadata):
        self.known_metadata = known_metadata
        self.docid = docid
#        self.i = shlaxtree.ShlaxIngestor(target=self)
        self.tree = None #unnecessary?
        self.root = None
        self.stack = []
        self.map = xpaths or TEI_XPaths
        self.metadata_paths = metadata_xpaths or TEI_MetadataXPaths
        self.v = OHCOVector.CompoundStack(types,parallel,docid,output)
        # OHCOVector should take an output file handle.
        self.extractors = []
        self.file_position = 0
        self.token_regex = token_regex
        self.non_nesting_tags = non_nesting_tags
        self.self_closing_tags = self_closing_tags
        self.pseudo_empty_tags = pseudo_empty_tags
        self.pushed_tags = {}
        self.depth_pushed = {}
        
    def parse(self,input):
        """Top level function for reading a file and printing out the output."""
        self.input = input
        p = ExpatWrapper(target=self)
        return p.parse(input)
#        self.i.feed(self.input.read())
#        return self.i.close()
        
    def parsebyline(self,input):
        self.input = input
        for line in self.input:
            self.i.feed(line)
        return self.i.close()

    def feed(self,*event):
        """Consumes a single event from the parse stream.
        
        Transforms "start","text", and "end" events into OHCOVector pushes, pulls, and attributes,
        based on the object and metadata Xpaths given to the constructor."""
        
        e_type, content, offset, name, attrib = event

        if e_type == "start":
            # Add every element to the tree and store a pointer to it in the stack.
            # The first element will be the root of our tree.
            if self.root is None: 
                self.root = et.Element(name,attrib) 
                new_element = self.root
            else:
                if name in self.non_nesting_tags:
                    tag_stack = [el.tag for el in self.stack]
                    if name in tag_stack:
                        pull_to = tag_stack.index(name)
                        tags_to_pull = tag_stack[pull_to:]
                        tags_to_pull.reverse()
                        for tag in tags_to_pull:
                            self.feed( "end","",offset,tag,{})
                new_element = et.SubElement(self.stack[-1],name,attrib)

            self.stack.append(new_element)
            # see if this Element should emit a new Record
            for xpath,ohco_type in self.map.items():
                if new_element in self.root.findall(xpath):
                    self.v.push(ohco_type,name,offset)
                    #print >> sys.stderr, "pushing %s for %s" % (ohco_type,name)
                    self.pushed_tags[name] = ohco_type
                    if name not in self.pseudo_empty_tags:
                        self.depth_pushed[len(self.stack)] = ohco_type
                    if ohco_type == 'doc':
                        for key,value in self.known_metadata.items():
                            self.v[ohco_type][key] = value                        

                    # Set up metadata extractors for the new Record
                    if ohco_type in self.metadata_paths:
                        for extractor,pattern,field in self.metadata_paths[ohco_type]:
                            self.extractors.append( (extractor(pattern,field,new_element,self.v[ohco_type]),len(self.stack))) 
                    break   # Don't check any other paths.
                
            # Extract any metadata in the attributes 
            utf8_attrib = {}
            for k,v in attrib.items():
                utf8_attrib[k] = v.encode("utf-8")                
            for ex,depth in self.extractors:
                ex(new_element,(e_type, content, offset, name, utf8_attrib))
                        
            # If self closing, immediately close the tag
            if name in self.self_closing_tags:
                self.feed("end","",offset,name,{})

        if e_type == "text":

            # Extract metadata if necessary.
            if self.stack:
                current_element = self.stack[-1]
                for ex,depth in self.extractors:
                    utf8_event = (e_type, content.encode("utf-8"), offset, name, attrib)
                    ex(current_element,utf8_event) # EXTRACTORS NEED TO USE NEW STACK API
                    # Should test whether to go on and tokenize or not.
                # Tokenize and emit tokens.  Still a bit hackish.
                # TODO: Tokenizer object shared with output formatter. 
                tokens = re.finditer(self.token_regex,content,re.U) # should put in a nicer tokenizer.
                for t in tokens:
                    if t.group(1):
                        # This technique is kind of a hack.  
                        # Would be more flexible to simply suppress tokenization in tagged word objects,
                        # then REQUIRE a filter to index token value.                        
                        if "word" in self.v and self.v["word"].name == "w":
                            self.v["word"].name = t.group(1).lower().encode("utf-8")
                        else:
                            # This will implicitly push a sentence if we aren't in one already.
                            self.v.push("word",t.group(1).lower().encode("utf-8"),offset + len(content[:t.start(1)].encode("utf-8")) )
                            self.v.pull("word",offset + len(content[:t.end(1)].encode("utf-8")))
                    elif t.group(2):
                        # a sentence should already be defined most of the time.
                        if "sent" not in self.v:
                            # but we'll make sure one is.
                            self.v.push("sent",t.group(2).encode("utf-8"),offset)
                        # if we have a sentence, set its name attribute to the punctuation that has now ended it.
                        self.v["sent"].name = t.group(2)
                        self.v.pull("sent",offset + len(content[:t.end(2)].encode("utf-8")))

        if e_type == "end":

            if self.stack: # All elements get pulled off the stack..
                if self.stack[-1].tag == name:

                    # This can go badly out of whack if you're just missing one end tag 
                    if name not in self.pseudo_empty_tags: # This should almost certainly be caught in the "start" event handler!
                        if len(self.stack) in self.depth_pushed:                        
                            # pseudo_empty_tags are popped off the XML stack, 
                            # but the records persist until another is pushed at the same level, 
                            # or a parent is pulled. Ideal for milestones, line breaks, etc.
                            ohco_type = self.depth_pushed[len(self.stack)]
                            self.v.pull(ohco_type,offset)
                            # del self.pushed_tags[old_element.tag]
                            del self.depth_pushed[len(self.stack)]
                            #for k,v in self.depth_pushed.items():
                            #    if v == ohco_type:
                            #        del self.depth_pushed[k]
                    old_element = self.stack.pop()
                    
                    # clean up any metadata extractors instantiated for this element.
                    current_depth = len(self.stack)
                    for ex,depth in self.extractors:
#                        print "%s vs %s" % (ex.context,old_element)
#                        if ex.context not in self.stack:
#                            print "removing"
                         if depth > current_depth:
                             self.extractors.remove((ex,depth))
#                    for ex,depth in self.extractors:
#                        print "%s:%s@%d" % (ex,ex.context,depth)

                    # prune the tree.
                    old_element.clear() # empty old element.
                    if self.stack: # if the old element had a parent:
                        del self.stack[-1][-1] # delete reference in parent                        
                    else: # otherwise, you've cleared out the whole tree
                        self.root = None
                    # Now that all references to the element are gone, Python will GC it at leisure.

        self.file_position = offset + len(content)


    def close(self):
        """Finishes parsing a document, and emits any objects still extant.
        
        Returns a max_id vector suitable for building a compression bit-spec in a loader."""
        # pull all extant objects.
        self.v.pull("doc",self.file_position)
        return self.v.v_max


if __name__ == "__main__":
    import sys
    did = 1
    files = sys.argv[1:]
    for docid, filename in enumerate(files,1):
        f = open(filename)
        print >> sys.stderr, "%d: parsing %s" % (docid,filename)
        p = StrictParser(output=sys.stdout,docid=docid,filename=filename)
#        p = Parser({"filename":filename},docid, non_nesting_tags = ["div1","div2","div3","p"],self_closing_tags = ["br","lb","ab"],output=sys.stdout)
#        p = Parser({"filename":filename},docid, non_nesting_tags = [],output=sys.stdout)
        p.parse(f)
        #print >> sys.stderr, "%s\n%d total tokens in %d unique types." % (spec,sum(counts.values()),len(counts.keys()))
