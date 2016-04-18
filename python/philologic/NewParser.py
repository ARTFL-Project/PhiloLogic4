import os
import re
import sys

from philologic import OHCOVector


class PlainTextParser(object):

    def __init__(self,
                 output,
                 docid,
                 filesize,
                 token_regex=r"(\w+)|([\.\?\!])",
                 xpaths=[("doc", "./")],
                 metadata_xpaths=[],
                 suppress_tags=[],
                 pseudo_empty_tags=[],
                 known_metadata={}):
        self.types = ["doc", "div1", "div2", "div3", "para", "sent", "word"]
        self.parallel_type = "page"
        self.output = output
        self.docid = docid
        ## Initialize an OHCOVector Stack. operations on this stack produce all parser output.
        self.v = OHCOVector.CompoundStack(self.types, self.parallel_type, docid, output)

        self.filesize = filesize

        self.token_regex = token_regex
        self.xpaths = xpaths[:]
        self.metadata_xpaths = metadata_xpaths[:]

        self.suppress_xpaths = suppress_tags
        self.pseudo_empty_tags = pseudo_empty_tags
        self.known_metadata = known_metadata

        self.buffer_position = 0
        self.buffers = []

        # List of global variables used for the tag handler
        self.line_count = 0
        self.bytes_read_in = 0
        self.in_the_text = False
        self.in_text_quote = False
        self.in_quote_text_tag = False
        self.do_this_para = True
        self.in_a_note = False
        self.no_deeper_objects = False
        self.in_line_group = False
        self.open_div1 = False
        self.open_div2 = False
        self.open_div3 = False
        self.open_para = False
        self.open_sent = False
        self.open_page = False
        self.line_group_break_sent = False
        self.in_tagged_sentence = False

    def parse(self, input):
        """Top level function for reading a file and printing out the output."""
        buffer_pos = 0
        byte_pos = 0
        self.input = input
        self.content = input.read().decode("utf-8")
        self.content = self.cleanup_content()

        # Begin by creating a document level object, just call it "text" for now.
        self.v.push("doc", "text", 0)

        # if the parser was created with known_metadata,
        # we can attach it to the newly created doc object here.
        # you can attach metadata to an object at any time between push() and pull().
        for k, v in self.known_metadata.iteritems():
            self.v["doc"][k] = v

        # Split content into a list on newlines.
        self.content = content.split('\n')

        for line in content:
            # Let's start indexing words and objects at either the <text
            # of the <docbody tag.  We can add more.

            if text_tag.search(line) or doc_body_tag.search(line) or body_tag.search(line):
                self.in_the_text = True

            self.line_count += 1

            if line.starswith('<'):
                self.bytes_read_in += len(line.encode('utf8'))
                # TODO : implement DUMPXPATHS
                if self.in_the_text:
                    self.tag_handler(line)
            else:
                # TODO wordhandler
                self.bytes_read_in += len(line.encode('utf8'))



        # Begin by creating a document level object, just call it "text" for now.
        self.v.push("doc", "text", 0)
        for k, v in self.known_metadata.items():
            # if the parser was created with known_metadata,
            # we can attach it to the newly created doc object here.
            # you can attach metadata to an object at any time between push() and pull().
            self.v["doc"][k] = v
        for tok in re.finditer(self.token_regex, content, re.U):
            # now just tokenize the entire text and push/pull word and sentence objects.
            if tok.group(1):
                tok_type = "word"
            elif tok.group(2):
                tok_type = "sent"

            tok_length = len(tok.group().encode("utf-8"))
            tok_start = len(content[buffer_pos:tok.start()].encode("utf-8"))
            tok_end = len(content[buffer_pos:tok.end()].encode("utf-8"))

            byte_start = byte_pos + tok_start
            byte_end = byte_pos + tok_end

            # for all tokens, push with byte_start and token content, pull with byte_end
            if tok_type == "word":
                self.v.push("word", tok.group(1).encode("utf-8"), byte_start)
                #                print >> sys.stderr,tok.group(1).encode("utf-8")
                self.v.pull("word", byte_end)
            elif tok_type == "sent":
                # a little hack--we don't know the punctuation mark that will end a sentence
                # until we encounter it--so instead, we let the push on "word" create a
                # implicit philo_virtual sentence, then change its name once we actually encounter
                # the punctuation token.
                if "sent" not in self.v:
                    self.v.push("sent", tok.group(2).encode("utf-8"), byte_start)
                self.v["sent"].name = tok.group(2).encode("utf-8")
                self.v.pull("sent", byte_end)
            buffer_pos = tok.end()
            byte_pos = byte_end
        self.v.pull("doc", self.filesize)

    def cleanup_content(self):
        """Run various clean-ups before parsing."""
        # Replace carriage returns with spaces since they can give us all kinds of difficulties.
        self.content = content.replace('\r', ' ')

        # Join hyphens
        self.content = join_hyphen_with_lb.sub("_" * len("\1"), content)
        self.content = join_hyphen.sub("_" * len("\1"), content)

        # Replace newlines with spaces.  Remember that we have seen lots of
        # tags with newlines, which can make a mess of things.
        self.content = content.replace('\n', ' ')

        # Abbreviation expander TODO...

        # An experimental inword tag spanner. For selected tags between letters, this replaces the tag with "_"
        # (in order to keep the byte count).  This is to allow indexing of words broken by tags.
        # TODO

        # TODO: TagWordDel
        # Delete tag data endtag set specified in the list @listoignore.
        # Replace with string of " "in order to keep the byte count.  This is
        # selection of things to NOT to index.

        # Add newlines to the beginning and end of all tags
        self.content = content.replace('<', '\n<').replace('>', '>\n')

    def tag_handler(self, tag):
        '''Tag handler for parser.'''

        byte_start = self.bytes_read_in - len(tag.encode('utf8'))

        # Handle <q> tags
        if text_tag.search(tag) and self.in_text_quote:
            self.in_quote_text_tag = True
        if closed_text_tag.search(tag):
            self.in_quote_text_tag = False
        if quote_tag.search(tag):
            self.in_text_quote = True
        if closed_quote_tag.search(tag):
            self.in_text_quote = False

        # Paragraphs
        # TODO: consistency with handling of self.no_deeper_objects variable in para type objects
        if parag_tag.search(tag) or parag_with_attrib_tag.search(tag):
            self.do_this_para = True
            if self.in_a_note:
                self.do_this_para = False
            if self.no_deeper_objects:
                self.do_this_para = False
            if self.do_this_para:
                if self.open_para:  # account for unclosed paragraph tags
                    para_byte_end = self.bytes_read_in - len(tag.encode('utf8'))
                    self.close_para(para_byte_end)
                self.v.push("para", byte_start)
                self.open_para = True
        if closed_para_tag.search(tag):
            self.close_para(self.bytes_read_in)

        # Notes: treat as para objects and set flag to not set paras in notes.
        # Currently treating them as distinct paragraphs.
        # TODO: what to when note has id= statement: like in Philo3?
        if note_tag.search(tag):
            self.open_para = True
            self.v.push("para", byte_start)
            self.in_a_note = True
        if closed_note_tag.search(tag):
            self.close_para(self.bytes_read_in)
            self.in_a_note = False

        # Epigraph: treat as paragraph objects
        if epigraph_tag.search(tag):
            self.open_para = True
            self.v.push("para", byte_start)
            self.no_deeper_objects = True
        if closed_epigraph_tag.search(tag):
            self.close_para(self.bytes_read_in)
            self.no_deeper_objects = False

        # LIST: treat as para objects
        if list_tag.search(tag) and not self.no_deeper_objects:
            self.open_para = True
            self.v.push("para", byte_start)
        # TODO: investigate why no closed tag handling in Philo3
        if closed_list_tag.search(tag):
            self.close_para(self.bytes_read_in)

        # SPEECH BREAKS: treat them as para objects
        if speaker_tag.search(tag):
            self.open_para = True
            self.v.push("para", byte_start)
            self.no_deeper_objects = True
        if closed_speaker_tag.search(tag):
            self.close_para(self.bytes_read_in)
            self.no_deeper_objects = False

        # ARGUMENT BREAKS: treat them as para objects
        if argument_tag.search(tag):
            self.open_para = True
            self.v.push("para", byte_start)
            self.no_deeper_objects = True
        if closed_argument_tag.search(tag):
            self.close_para(self.bytes_read_in)
            self.no_deeper_objects = False

        # OPENER BREAKS: treat them as para objects
        if opener_tag.search(tag):
            self.open_para = True
            self.v.push("para", byte_start)
            self.no_deeper_objects = True
        if closed_opener_tag.search(tag):
            self.close_para(self.bytes_read_in)
            self.no_deeper_objects = False

        # CLOSER BREAKS: treat them as para objects
        if closer_tag.search(tag):
            self.open_para = True
            self.v.push("para", byte_start)
            self.no_deeper_objects = True
        if closed_closer_tag.search(tag):
            self.close_para(self.bytes_read_in)
            self.no_deeper_objects = False

        # STAGE DIRECTIONS: treat them as para objects
        if stage_tag.search(tag) and not self.no_deeper_objects:
            self.open_para = True
            self.v.push("para", byte_start)
        if closed_stage_tag.search(tag):
            self.close_para(self.bytes_read_in)

        # CAST LIST: treat them as para objects
        if castlist_tag.search(tag):
            self.open_para = True
            self.v.push("para", byte_start)
        if closed_castlist_tag.search(tag):
            self.close_para(self.bytes_read_in)

        # PAGE BREAKS: this updates the currentpagetag or sets it to "na" if not found.
        # TODO: handling of attributes
        if page_tag.search(tag):
            if self.open_page:
                self.v.pull("page", self.bytes_read_in)
                self.open_page = False
            self.v.pull("page", byte_start)
            n_attrib = n_attribute.search(tag)
            if n_attrib:
                n = n_attrib.group()[0]
                n = n.replace(' ', '_').replace('-', '_').lower()
                if not n:
                    n = "na"
            else:
                n = "na"
            self.v["page"]["n"] = n
            self.open_page = True

        # LINE GROUP TAGS: treat linegroups same a paragraphs, set or unset the global
        # variable self.in_line_group.
        if line_group_tag.search(tag) and not self.no_deeper_objects:
            if self.line_group_break_sent:
                self.in_line_group = True
            self.open_para = True
            self.v.push("para", byte_start)
        if closed_line_group.search(tag):
            self.in_line_group = False
            self.close_para(self.bytes_read_in)

        # END LINE TAG: use this to break "sentences" if self.in_line_group.  This is
        # if to set searching in line groups to lines rather than sentences.
        # TODO: not sure I got this right...
        if line_tag.search(tag):
            if self.in_line_group and self.line_group_break_sent:
                self.v.push("sent", self.byte_start)
                self.v.pull("sent", self.bytes_read_in)

        # SENTENCE TAG: <s> </s>.  We have never seen a sample of these
        # but let's add the required code to note the beginning of a new
        # sentence and to turn off automatic sentence tagging
        if sentence_tag.search(tag):
            if self.open_sent or self.in_tagged_sentence:
                self.v.pull("sent", byte_start)
            self.v.push("sent", byte_start)
            self.in_tagged_sentence = True
            self.open_sent = True
        if closed_sentence_tag.search(tag):
            self.v.pull("sent", self.bytes_read_in)
            self.in_tagged_sentence = False
            self.open_sent = False

        # TODO: handle docbody

        # FRONT: Treat <front as a <div and set <divs in front as being one div level deeper.
        if front_tag.search(tag):
            if self.open_div1:
                self.close_div1(byte_start)
            self.v.push("div1", byte_start)
            self.open_div1 = True
        if closed_front_tag.search(tag):
            self.close_div1(self.bytes_read_in)


    def close_para(self, para_byte_end):
        """Close paragraph objects."""
        if self.open_sent:
            self.v.pull("sent", para_byte_end)
        self.v.pull("para", para_byte_end)
        self.open_para = False

    def close_div3(self, byte_end):
        if self.open_para:
            self.close_para(byte_end)
        self.v.push("div3", byte_end)
        self.open_div3 = False

    def close_div2(self, byte_end):
        if self.open_para:
            self.close_para(byte_end)
        if self.open_div3:
            self.close_div3(byte_end)
        self.v.push("div1", byte_end)
        self.open_div1 = False

    def close_div1(self, byte_end):
        if self.open_para:
            self.close_para(byte_end)
        if self.open_div2:
            self.close_div2(byte_end)
        if self.open_div3:
            self.close_div3(byte_end)
        self.v.push("div1", byte_end)
        self.open_div1 = False

# Pre-compiled regexes used for parsing
join_hyphen_with_lb = re.compile(r'(\&shy;[\n \t]*<lb\/>)', re.U | re.I | re.M)
join_hyphen = re.compile(r'(\&shy;[\n \t]*)', re.U | re.I | re.M)
in_word_tag_del = re.compile(r'([A-Za-z;])($e)([A-Za-z&])', re.U | re.I | re.M)
text_tag = re.compile(r'<text\W', re.U | re.I)
closed_text_tag = re.compile(r'</text\W', re.U | re.I)
doc_body_tag = re.compile(r'<docbody', re.U | re.I)
body_tag = re.compile(r'<body\W', re.U | re.I)
quote_tag = re.compile(r'<q[ >]', re.U | re.I)
closed_quote_tag = re.compile(r'</q>', re.U | re.I)
parag_tag = re.compile(r'<p>', re.U | re.I)
parag_with_attrib_tag = re.compile(r'<p ', re.U | re.I)
closed_para_tag = re.compile(r'</p>', re.U | re.I)
note_tag = re.compile(r'<note\W', re.U | re.I)
closed_note_tag = re.compile(r'</note>', re.U | re.I)
epigraph_tag = re.compile(r'<epigraph\W', re.U | re.I)
closed_epigraph_tag = re.compile(r'</epigraph>', re.U | re.I)
list_tag = re.compile(r'<list ', re.U | re.I)
closed_list_tag = re.compile(r'</list>', re.U | re.I)
speaker_tag = re.compile(r'<sp\W', re.U | re.I)
closed_speaker_tag = re.compile(r'</sp>', re.U | re.I)
argument_tag = re.compile(r'<argument\W', re.U | re.I)
closed_argument_tag = re.compile(r'</argument>', re.U | re.I)
opener_tag = re.compile(r'<opener\W', re.U | re.I)
closed_opener_tag = re.compile(r'</opener\W', re.U | re.I)
closer_tag = re.compile(r'<closer\W', re.U | re.I)
closed_closer_tag = re.compile(r'</closer\W', re.U | re.I)
stage_tag = re.compile(r'<stage\W', re.U | re.I)
closed_stage_tag = re.compile(r'</stage\W', re.U | re.I)
castlist_tag = re.compile(r'<castlist\W', re.U | re.I)
closed_castlist_tag = re.compile(r'</castlist\W', re.U | re.I)
page_tag = re.compile(r'<pb\W', re.U | re.I)
n_attribute = re.compile(r'n="([^"]*)', re.U | re.I)
line_group_tag = re.compile(r'<lg\W', re.U | re.I)
closed_line_group = re.compile(r'</lg\W', re.U | re.I)
line_tag = re.compile(r'<l\W', re.U | re.I)
closed_line_tag = re.compile(r'</l\W', re.U | re.I)
sentence_tag = re.compile(r'<s\W', re.U | re.I)
closed_sentence_tag = re.compile(r'</s\W', re.U | re.I)
front_tag = re.compile(r'<front\W', re.U | re.I)
closed_front_tag = re.compile(r'</front\W', re.U | re.I)


if __name__ == "__main__":
    for docid, fn in enumerate(sys.argv[1:], 1):
        print >> sys.stderr, docid, fn
        size = os.path.getsize(fn)
        fh = open(fn)
        parser = PlainTextParser(sys.stdout,
                                 docid,
                                 size,
                                 token_regex=r"(\w+)|([\.\?\!])",
                                 known_metadata={"filename": fn})
        parser.parse(fh)
