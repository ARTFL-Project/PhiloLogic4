

from lxml import etree
from xml.parsers import expat
import sys
import os
import re
import io
from philologic import OHCOVector


class ExpatWrapper:

    def start_element(self, name, attrs):
        buffer = self.p.GetInputContext()
        tag_end = buffer.index(">") + 1
        content = buffer[:tag_end]
        name = re.sub(r"^.*?:", "", name)
        #        utf8_attrs = {}
        for k, v in list(attrs.items()):
            no_ns_k = re.sub(r"^.*?:", "", k)
            if no_ns_k != k:
                del attrs[k]
                attrs[no_ns_k] = v
#            utf8_attrs[k] = v.encode("utf-8")
        self.target.feed("start", content, self.p.CurrentByteIndex, name, attrs.copy())

    def end_element(self, name):
        closer = "</%s>" % name.encode("utf-8")
        closer_len = len(closer)
        buffer = self.p.GetInputContext()
        name = re.sub(r"^.*?:", "", name)
        #        print >> sys.stderr, buffer[:closer_len], " vs ", closer, " ?"
        if buffer[:closer_len] == closer:
            #            print >> sys.stderr, "MATCH"
            content_length = closer_len
        else:
            #            print >> sys.stderr, "NO MATCH"
            content_length = 0
        content = buffer[:content_length]
        self.target.feed("end", content, self.p.CurrentByteIndex + content_length, name, None)

    def char_data(self, data):
        data_len = len(data.encode("utf-8"))
        self.target.feed("text", data, self.p.CurrentByteIndex, None, None)

    def __init__(self, target):
        self.target = target
        self.p = expat.ParserCreate()
        self.p.StartElementHandler = self.start_element
        self.p.EndElementHandler = self.end_element
        self.p.CharacterDataHandler = self.char_data
        self.p.buffer_text = False

    def parse(self, file):
        self.p.ParseFile(file)
        return self.target.close()


class Parser(object):

    def __init__(self,
                 output,
                 docid,
                 filesize,
                 token_regex=r"(\w+)|([\.\?\!])",
                 xpaths=[("doc", "./")],
                 metadata_xpaths=[],
                 suppress_tags=[],
                 pseudo_empty_tags=[],
                 words_to_index=[],
                 known_metadata={}):
        self.types = ["doc", "div1", "div2", "div3", "para", "sent", "word"]
        self.parallel_type = "page"
        self.output = output
        self.docid = docid
        self.filesize = filesize
        self.v = OHCOVector.CompoundStack(self.types, self.parallel_type, docid, output)

        self.token_regex = token_regex
        self.xpaths = xpaths[:]
        self.metadata_xpaths = metadata_xpaths[:]

        self.suppress_xpaths = suppress_tags
        self.pseudo_empty_tags = pseudo_empty_tags
        self.known_metadata = known_metadata

        self.stack = []
        self.root = None
        self.handlers = {}
        self.buffer_position = 0
        self.buffers = []

    def parse(self, input):
        """Top level function for reading a file and printing out the output."""
        self.input = input
        lexer = ExpatWrapper(self)
        return lexer.parse(self.input)

    def make_extractor(self, new_element, obj_type, mxp, field):
        """Constructs metadata-xpath extraction callbacks.  Called from feed() when a new object is constructed.
        Called on every descendant object."""
        destination = self.v[
            obj_type
        ]  # Note that this object will still exist after the OHCOVector has printed and discarded it.
        # Thus, extracting to a 'closed" object will silently discard values.  Which I think is the least bad option.
        attr_pattern_match = re.search(r"\/?@([^\/\[\]]+)$", mxp)
        if attr_pattern_match:
            xp_prefix = mxp[:attr_pattern_match.start(0)]
            attr_name = attr_pattern_match.group(1).decode("utf-8")

            def extract_attr(future_event, future_element):
                if future_event[0] == "start":
                    #                    if future_element in new_element.findall(xp_prefix):
                    if new_element.findall(xp_prefix) == [future_element]:
                        if future_element.get(attr_name, ""):
                            destination[field] = future_element.get(attr_name)
                            return True
                return False

            return extract_attr
        else:
            value_buffer = []

            def extract_text(future_event, future_element):
                if future_event[0] == "text":
                    #                    if future_element in new_element.findall(mxp):
                    if new_element.findall(mxp):
                        value_buffer.append(future_event[1])
#                        print >> sys.stderr, "CAPTURE", repr(value_buffer)
                if future_event[0] == "end":
                    if new_element.findall(mxp) == [future_element]:
                        #                        print >> sys.stderr, "CLOSE ELEMENT"
                        if destination.get(field, ""):
                            #                            print >> sys.stderr, "CONFLICT?"
                            pass
                        else:
                            destination[field] = "".join(value_buffer)
#                            print >> sys.stderr, "SUCCESS", field, destination[field], repr(value_buffer)
# return True so that the Parser can remove the callback.
                        return True
                return False

            return extract_text

    def make_suppressor(self, new_element, path):
        """Constructs a tokenization suppression callback.  Used in feed() when handling text events"""

        def suppress_tokens(future_event, future_element):
            if future_event[0] == "text":
                if future_element in new_element.findall(path):
                    #                    print >> sys.stderr, "SUPPRESS", path
                    return False
            return True

        return suppress_tokens

    def flush_buffer(self):
        """Passes through all current content buffers, tokenizing and calculating correct byte offsets,
        and emitting word records as necessary.  Called from feed and the cleanup() callback."""
        if self.buffers == []:
            return
        temp_buffer = "".join(buf["content"] for buf in self.buffers)
        temp_position = 0
        offset = self.buffers[0]["offset"]
        for tok in re.finditer(self.token_regex, temp_buffer, re.U):
            if tok.group(1):
                tok_type = "word"
            elif tok.group(2):
                tok_type = "sent"

            tok_length = len(tok.group().encode("utf-8"))
            tok_start = len(temp_buffer[:tok.start()].encode("utf-8"))
            tok_end = len(temp_buffer[:tok.end()].encode("utf-8"))
            while (tok_start >= (temp_position + self.buffers[0]["length"])):
                temp_position += self.buffers[0]["length"]
                discard = self.buffers.pop(0)
                offset = self.buffers[0]["offset"]
            start = offset + tok_start - temp_position
            while (tok_end >= self.buffers[0]["length"] + temp_position):
                temp_position += self.buffers[0]["length"]
                discard = self.buffers.pop(0)
                if self.buffers:
                    offset = self.buffers[0]["offset"]
                # we have to catch the case where the last word goes right up to the end of the last buffer, which is surprisingly rare in TEI XML.
                else:
                    offset = discard["offset"] + discard["length"]
                    break
            end = offset + tok_end - temp_position
            if tok_type == "word":
                self.v.push("word", tok.group(1).encode("utf-8"), start)
                #                print >> sys.stderr,tok.group(1).encode("utf-8")
                self.v.pull("word", end)
            elif tok_type == "sent":
                if "sent" not in self.v:
                    self.v.push("sent", tok.group(2).encode("utf-8"), offset)
                self.v["sent"].name = tok.group(2).encode("utf-8")
                self.v.pull("sent", end)
        self.buffers = []
#            print >> self.output, tok_type, tok.group().encode("utf-8"), start, end

    def feed(self, *event):
        e_type, content, offset, name, attrib = event
        #        print >> sys.stderr, repr(event)
        if e_type == "start":
            #create a new element, and initalize the tree if necessary
            if self.root is None:
                self.root = etree.Element(name, attrib)
                new_element = self.root
            else:
                new_element = etree.SubElement(self.stack[-1], name, attrib)
            self.stack.append(new_element)

            for obj_type, xpath in self.xpaths:
                # test xpaths and create new objects for the current element
                if new_element in self.root.findall(xpath):
                    self.flush_buffer()
                    #                    print obj_type,repr(new_element)
                    self.v.push(obj_type, name, offset)
                    if obj_type == "doc":
                        for key, value in list(self.known_metadata.items()):
                            self.v[obj_type][key] = value

                    # should not attach cleanup for page and milestone objects
                    def cleanup(event, element):
                        if event[0] == "end":
                            if id(element) == id(new_element):
                                self.flush_buffer()

                                #                                print "DONE:",obj_type,repr(new_element)
                                self.v.pull(obj_type, event[2])
                                return True
                        return False
#                    self.handlers[new_element] = [cleanup]

                    self.handlers[new_element] = []
                    for m_obj_type, m_xpath, field in self.metadata_xpaths:
                        if m_obj_type == obj_type:
                            self.handlers[new_element] += [self.make_extractor(new_element, m_obj_type, m_xpath, field)]
#                            print >> sys.stderr, "adding handler for ", m_obj_type, m_xpath, field, "to", new_element
                    self.handlers[new_element] += [cleanup]
                    #                    print >> sys.stderr, self.handlers[new_element]
                    # only emit one object per element.
                    break

            # check for metadata on the new element.
            for open_object in list(self.handlers.keys()):
                #                print >> sys.stderr, open_object, self.handlers[open_object]
                to_remove = []
                for handler in self.handlers[open_object]:
                    #                    print >> sys.stderr, "running ", handler
                    #                    handler(event,new_element)
                    if handler(event, new_element):
                        # If a handler returns True in the end phase, delete it to prevent future evaluation.
                        #                        print >> sys.stderr, "removing", handler
                        to_remove.append(handler)
#                        self.handlers[open_object].remove(handler)
#                        print >> sys.stderr, self.handlers[open_object]
                for handler in to_remove:
                    self.handlers[open_object].remove(handler)
            # objects that don't correspond to real elements can't attach handlers, or clean themselves up.
            # Let OHCOVector handle them numerically instead.
            if (obj_type == self.parallel_type) or (new_element.tag in self.pseudo_empty_tags):
                self.handlers[new_element] = []

        if e_type == "text":
            if self.stack:
                # check for metadata handlers:
                for open_object in list(self.handlers.keys()):
                    for handler in self.handlers[open_object]:
                        handler(event, self.stack[-1])
                #check if we're in a non-indexed element:
                status = True
                for sup_path in self.suppress_xpaths:
                    if self.root.findall(sup_path):
                        status = False
                if status:
                    self.buffers.append({"content": content, "offset": offset, "length": len(content.encode("utf-8"))})
                # should test buffer size here so that we don't eat all memory, in the worst-case.  add to options later.

        if e_type == "end":
            #            print >> sys.stderr, repr(event)
            if name != self.stack[-1].tag:
                #expat should die before you ever get here.  Just to be safe...
                print("TAG MISMATCH:", repr(new_element), repr(stack))
                sys.exit()
            else:
                popped = self.stack.pop()

                # do any cleanup for the element that just ended
                for open_object in list(self.handlers.keys()):
                    for handler in self.handlers[open_object]:
                        #                        print >> sys.stderr, handler, [c.cell_contents for c in handler.func_closure]
                        if handler(event, popped):
                            # If a handler returns True in the end phase, delete it to prevent future evaluation.
                            self.handlers[open_object].remove(handler)

                # clear out the removed element, and delete it's reference in its parent.
                if popped in self.handlers:
                    del self.handlers[popped]
                popped.clear()
                if self.stack:
                    del self.stack[-1][-1]

    def close(self):
        # cleans up any still open philo-objects; this should only happen for pages that don't map to XML elements, like pages or milestones.
        self.v.pull("page", self.filesize
                   )  # should implement this automatically in doc pull.  Important for multi-doc files.
        self.v.pull("doc", self.filesize)  # This does nothing if all elements are already closed.
        return self.v.v_max

DefaultWordRegex = r"([\w]+)"
DafaultPunctRegex = r"([\.?!])"

DefaultTokenRegex = "%s|%s" % (DefaultWordRegex, DafaultPunctRegex)

DefaultXPaths = [
    ("doc", "."), ("div", ".//div"), ("div", ".//div1"), ("div", ".//front"), ("div", ".//note"), ("div", ".//div2"),
    ("div", ".//div3"), ("para", ".//text//p"), ("para", ".//body//p"), ("para", ".//sp"), ("para", ".//lg"),
    ("para", ".//epigraph"), ("para", ".//argument"), ("para", ".//postscript"), ("page", ".//pb")
]

DefaultMetadataXPaths = {
    # Metadata per type.  '.' is in this case the base element for the type, as specified in XPaths above.
    # MUST MUST MUST BE SPECIFIED IN OUTER TO INNER ORDER--DOC FIRST, WORD LAST

    ####################
    # DOC LEVEL XPATHS #
    ####################
    "doc": {
        "author": [
            ".//sourceDesc/bibl/author[@type='marc100']",
            ".//sourceDesc/bibl/author[@type='artfl']",
            ".//sourceDesc/bibl/author",
            ".//titleStmt/author",
            ".//sourceDesc/biblStruct/monogr/author/name",
            ".//sourceDesc/biblFull/titleStmt/author",
            ".//sourceDesc/biblFull/titleStmt/respStmt/name",
            ".//sourceDesc/biblFull/titleStmt/author",
            ".//sourceDesc/bibl/titleStmt/author",
        ],
        "title": [
            ".//sourceDesc/bibl/title[@type='marc245']",
            ".//sourceDesc/bibl/title[@type='artfl']",
            ".//sourceDesc/bibl/title",
            ".//titleStmt/title",
            ".//sourceDesc/bibl/titleStmt/title",
            ".//sourceDesc/biblStruct/monogr/title",
            ".//sourceDesc/biblFull/titleStmt/title",
        ],
        "author_dates": [
            ".//sourceDesc/bibl/author/date",
            ".//titlestmt/author/date",
        ],
        "create_date": [
            ".//profileDesc/creation/date",
            ".//fileDesc/sourceDesc/bibl/imprint/date",
            ".//sourceDesc/biblFull/publicationStmt/date",
            ".//profileDesc/dummy/creation/date",
            ".//fileDesc/sourceDesc/bibl/creation/date",
        ],
        "publisher": [
            ".//sourceDesc/bibl/imprint[@type='artfl']",
            ".//sourceDesc/bibl/imprint[@type='marc534']",
            ".//sourceDesc/bibl/imprint/publisher",
            ".//sourceDesc/biblStruct/monogr/imprint/publisher/name",
            ".//sourceDesc/biblFull/publicationStmt/publisher",
            ".//sourceDesc/bibl/publicationStmt/publisher",
            ".//sourceDesc/bibl/publisher",
            ".//publicationStmt/publisher",
            ".//publicationStmp",
        ],
        "pub_place": [
            ".//sourceDesc/bibl/imprint/pubPlace",
            ".//sourceDesc/biblFull/publicationStmt/pubPlace",
            ".//sourceDesc/biblStruct/monog/imprint/pubPlace",
            ".//sourceDesc/bibl/pubPlace",
            ".//sourceDesc/bibl/publicationStmt/pubPlace",
        ],
        "pub_date": [
            ".//sourceDesc/bibl/imprint/date",
            ".//sourceDesc/biblStruct/monog/imprint/date",
            ".//sourceDesc/biblFull/publicationStmt/date",
            ".//sourceDesc/bibFull/imprint/date",
            ".//sourceDesc/bibl/date",
            ".//text/front/docImprint/acheveImprime",
        ],
        "extent": [
            ".//sourceDesc/bibl/extent",
            ".//sourceDesc/biblStruct/monog//extent",
            ".//sourceDesc/biblFull/extent",
        ],
        "editor": [
            ".//sourceDesc/bibl/editor",
            ".//sourceDesc/biblFull/titleStmt/editor",
            ".//sourceDesc/bibl/title/Stmt/editor",
        ],
        "identifiers": [
            ".//publicationStmt/idno"
        ],
        "text_genre": [
            ".//profileDesc/textClass/keywords[@scheme='genre']/term",
            ".//SourceDesc/genre",
        ],
        "keywords": [
            # keywords
            ".//profileDesc/textClass/keywords/list/item",
        ],
        "language": [
            # language
            ".//profileDesc/language/language",
        ],
        "notes": [
            # notes
            ".//fileDesc/notesStmt/note",
            ".//publicationStmt/notesStmt/note",
        ],
        "auth_gender": [

            # auth_gender
            ".//publicationStmt/notesStmt/note",
        ],
        "collection": [
            # collection
            ".//seriesStmt/title",
        ],
        "period": [
            # period
            ".//profileDesc/textClass/keywords[@scheme='period']/list/item",
            ".//SourceDesc/period",
        ],
        "text_form": [
            # text_form
            ".//profileDesc/textClass/keywords[@scheme='form']/term",
        ],
        "structure": [
            # structure
            ".//SourceDesc/structure",
        ]
    }
}

if __name__ == "__main__":
    for docid, fn in enumerate(sys.argv[1:], 1):
        print(docid, fn, file=sys.stderr)
        size = os.path.getsize(fn)
        fh = open(fn)
        parser = Parser(sys.stdout,
                        docid,
                        size,
                        token_regex=r"(\w+)|([\.\?\!])",
                        xpaths=DefaultXPaths,
                        metadata_xpaths=DefaultMetadataXPaths,
                        suppress_tags=["teiheader", "head"])
        lexer = ExpatWrapper(parser)
        lexer.parse(fh)
