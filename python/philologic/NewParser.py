import os
import re
import sys

from philologic import OHCOVector


class XMLParser(object):

    def __init__(self,
                 output,
                 docid,
                 filesize,
                 token_regex=r"(\w+)|([\.\?\!])",
                 xpaths=[("doc", "./")],
                 metadata_xpaths=[],
                 suppress_tags=[],
                 pseudo_empty_tags=[],
                 known_metadata=["doc", "div1", "div2", "div3", "para", "sent", "word"]):
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

        # In a <div, how far to look ahead for a <head.
        self.head_look_ahead_lines = 7

        self.get_multiple_div_heads = 1  # TODO: remove??

        # Set to 1 to break words on apostrophe.  Probably True for French.
        self.break_apost = False

        # List of global variables used for the tag handler
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
        self.got_a_div = False
        self.got_a_para = False

    def parse(self, input):
        """Top level function for reading a file and printing out the output."""
        self.input = input
        self.content = input.read().decode("utf-8")
        if div_tag.search(self.content):
            self.got_a_div = True
        if para_tag(self.content):
            self.got_a_para = True
        self.content = self.cleanup_content()

        # Begin by creating a document level object, just call it "text" for now.
        self.v.push("doc", "text", 0)

        # if the parser was created with known_metadata,
        # we can attach it to the newly created doc object here.
        # you can attach metadata to an object at any time between push() and pull().
        for k, v in self.known_metadata.iteritems():
            self.v["doc"][k] = v

        # Split content into a list on newlines.
        self.content = self.content.split('\n')

        self.line_count = 0
        for line in self.content:
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

        self.v.pull("doc", self.filesize)

    def cleanup_content(self):
        """Run various clean-ups before parsing."""
        # Replace carriage returns with spaces since they can give us all kinds of difficulties.
        self.content = self.content.replace('\r', ' ')

        # Join hyphens
        # TODO : len() does not work as intented below
        self.content = join_hyphen_with_lb.sub(lambda match: "_" * len(match.group(1)), self.content)
        self.content = join_hyphen.sub(lambda match: "_" * len(match.group(1)), self.content)

        # Replace newlines with spaces.  Remember that we have seen lots of
        # tags with newlines, which can make a mess of things.
        self.content = self.content.replace('\n', ' ')

        # Abbreviation expander TODO...

        # An experimental inword tag spanner. For selected tags between letters, this replaces the tag with "_"
        # (in order to keep the byte count).  This is to allow indexing of words broken by tags.
        # TODO

        # TODO: TagWordDel
        # Delete tag data endtag set specified in the list @listoignore.
        # Replace with string of " "in order to keep the byte count.  This is
        # selection of things to NOT to index.

        # Add newlines to the beginning and end of all tags
        self.content = self.content.replace('<', '\n<').replace('>', '>\n')

    def tag_handler(self, tag):
        '''Tag handler for parser.'''

        byte_start = self.bytes_read_in - len(tag.encode('utf8'))
        tag_name = tag_matcher.findall(tag)[0]

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
                self.v.push("para", tag_name, byte_start)
                self.get_attributes(tag, "para")
                self.open_para = True
        if closed_para_tag.search(tag):
            self.close_para(self.bytes_read_in)

        # Notes: treat as para objects and set flag to not set paras in notes.
        # Currently treating them as distinct paragraphs.
        # TODO: what to when note has id= statement: like in Philo3?
        if note_tag.search(tag):
            self.open_para = True
            self.v.push("para", tag_name, byte_start)
            self.get_attributes(tag, "para")
            self.in_a_note = True
        if closed_note_tag.search(tag):
            self.close_para(self.bytes_read_in)
            self.in_a_note = False

        # Epigraph: treat as paragraph objects
        if epigraph_tag.search(tag):
            self.open_para = True
            self.v.push("para", byte_start)
            self.get_attributes(tag, "para")
            self.no_deeper_objects = True
        if closed_epigraph_tag.search(tag):
            self.close_para(self.bytes_read_in)
            self.no_deeper_objects = False

        # LIST: treat as para objects
        if list_tag.search(tag) and not self.no_deeper_objects:
            self.open_para = True
            self.v.push("para", tag_name, byte_start)
            self.get_attributes(tag, "para")
        # TODO: investigate why no closed tag handling in Philo3
        if closed_list_tag.search(tag):
            self.close_para(self.bytes_read_in)

        # SPEECH BREAKS: treat them as para objects
        if speaker_tag.search(tag):
            self.open_para = True
            self.v.push("para", tag_name, byte_start)
            self.get_attributes(tag, "para")
            self.no_deeper_objects = True
        if closed_speaker_tag.search(tag):
            self.close_para(self.bytes_read_in)
            self.no_deeper_objects = False

        # ARGUMENT BREAKS: treat them as para objects
        if argument_tag.search(tag):
            self.open_para = True
            self.v.push("para", tag_name, byte_start)
            self.get_attributes(tag, "para")
            self.no_deeper_objects = True
        if closed_argument_tag.search(tag):
            self.close_para(self.bytes_read_in)
            self.no_deeper_objects = False

        # OPENER BREAKS: treat them as para objects
        if opener_tag.search(tag):
            self.open_para = True
            self.v.push("para", tag_name, byte_start)
            self.get_attributes(tag, "para")
            self.no_deeper_objects = True
        if closed_opener_tag.search(tag):
            self.close_para(self.bytes_read_in)
            self.no_deeper_objects = False

        # CLOSER BREAKS: treat them as para objects
        if closer_tag.search(tag):
            self.open_para = True
            self.v.push("para", tag_name, byte_start)
            self.get_attributes(tag, "para")
            self.no_deeper_objects = True
        if closed_closer_tag.search(tag):
            self.close_para(self.bytes_read_in)
            self.no_deeper_objects = False

        # STAGE DIRECTIONS: treat them as para objects
        if stage_tag.search(tag) and not self.no_deeper_objects:
            self.open_para = True
            self.v.push("para", tag_name, byte_start)
            self.get_attributes(tag, "para")
        if closed_stage_tag.search(tag):
            self.close_para(self.bytes_read_in)

        # CAST LIST: treat them as para objects
        if castlist_tag.search(tag):
            self.open_para = True
            self.v.push("para", tag_name, byte_start)
            self.get_attributes(tag, "para")
        if closed_castlist_tag.search(tag):
            self.close_para(self.bytes_read_in)

        # PAGE BREAKS: this updates the currentpagetag or sets it to "na" if not found.
        # TODO: handling of attributes
        if page_tag.search(tag):
            if self.open_page:
                self.v.pull("page", self.bytes_read_in)
                self.open_page = False
            self.v.pull("page", tag_name, byte_start)
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
            self.v.push("para", tag_name, byte_start)
            self.get_attributes(tag, "para")
        if closed_line_group.search(tag):
            self.in_line_group = False
            self.close_para(self.bytes_read_in)

        # END LINE TAG: use this to break "sentences" if self.in_line_group.  This is
        # if to set searching in line groups to lines rather than sentences.
        # TODO: not sure I got this right...
        if line_tag.search(tag):
            if self.in_line_group and self.line_group_break_sent:
                self.v.push("sent", tag_name, self.byte_start)
                self.v.pull("sent", self.bytes_read_in)

        # SENTENCE TAG: <s> </s>.  We have never seen a sample of these
        # but let's add the required code to note the beginning of a new
        # sentence and to turn off automatic sentence tagging
        if sentence_tag.search(tag):
            if self.open_sent or self.in_tagged_sentence:
                self.v.pull("sent", tag_name, byte_start)  # should cache name
            self.v.push("sent", tag_name, byte_start)
            self.in_tagged_sentence = True
            self.open_sent = True
        if closed_sentence_tag.search(tag):
            self.v.pull("sent", self.bytes_read_in)
            self.in_tagged_sentence = False
            self.open_sent = False

        # TODO: handle docbody

        # FRONT: Treat <front as a <div
        # TODO : test for inner divs as in Philo3???
        if front_tag.search(tag):
            if self.open_div1:
                self.close_div1(byte_start)
            self.v.push("div1", tag_name, byte_start)
            self.get_attributes(tag, "div1")
            self.open_div1 = True
        if closed_front_tag.search(tag):
            self.close_div1(self.bytes_read_in)

        # BODY TAG: Let's set it as a <div object if we have no divs in the document.
        # These tend to carry on as FRONTMATTER. Don't have to check for lower divs, etc.
        if body_tag.search(tag) and not self.got_a_div:
            self.push("div1", tag_name, byte_start)

    def close_sent(self, byte_end):
        """Close sentence objects."""
        self.v.pull("sent", byte_end)
        self.open_sent = False

    def close_para(self, byte_end):
        """Close paragraph objects."""
        if self.open_sent:
            self.close_sent(byte_end)
        self.v.pull("para", byte_end)
        self.open_para = False

    def close_div3(self, byte_end):
        """Close div3 objects."""
        if self.open_para:
            self.close_para(byte_end)
        self.v.push("div3", byte_end)
        self.open_div3 = False

    def close_div2(self, byte_end):
        """Close div2 objects."""
        if self.open_div3:
            self.close_div3(byte_end)
        self.v.push("div2", byte_end)
        self.open_div1 = False

    def close_div1(self, byte_end):
        """Close div1 objects."""
        if self.open_div2:
            self.close_div2(byte_end)
        self.v.push("div1", byte_end)
        self.open_div1 = False

    def get_attributes(self, tag, object_type):
        """Find all attributes for any given tag and attach metadata to element."""
        for attrib, value in attrib_matcher.findall(tag):
            self.v[object_type][attrib] = value

    def get_div_head(self, tag):
        """Get div head."""
        get_head_count = self.get_multiple_div_heads
        read_more = False
        look_ahead = self.line_count
        local_line_count = 0
        overflow_trap = 0
        div_head = ""
        while not read_more and local_line_count < self.head_look_ahead_lines:
            look_ahead += 1
            next_line = self.content[look_ahead]
            local_line_count += 1
            next_line = head_self_close_tag.sub("", next_line)
            if div_tag.search(next_line) or closed_div_tag.search(next_line):
                break  # don't go past an open or close <div.
            if head_tag.search(next_line):
                read_more = True
            if read_more:
                while read_more:
                    look_ahead += 1
                    overflow_trap += 1
                    next_line = self.content[look_ahead]
                    if closed_head_tag.search(next_line):
                        read_more = False
                        if self.get_multiple_div_heads:
                            local_line_count = 2
                            get_head_count -= 1
                        else:
                            local_line_count = self.head_look_ahead_lines + 1
                    elif overflow_trap > 10:  # Overflow trap in case you miss </head
                        read_more = False
                        local_line_count = self.head_look_ahead_lines + 1
                    else:
                        div_head += next_line + " "
        if div_head:
            div_head = self.clear_char_ents(div_head)

    def clear_char_ents(self, text):
        """Replaces a selected set of SGML character ents with spaces in order to keep the byte count right."""
        # We would want to read a list of character ents that should NOT be considered
        # valid for including in words or, more likely, a list of VALID characters from a general table.
        if self.break_apost:
            text = break_apost.sub(lambda match: "," + " " * len(match.group(1) - 1))
        for regex in entity_regex:
            text = regex.sub(lambda match: " " * len(match.group(1)))
        return text

# Pre-compiled regexes used for parsing
join_hyphen_with_lb = re.compile(r'(\&shy;[\n \t]*<lb\/>)', re.U | re.I | re.M)
join_hyphen = re.compile(r'(\&shy;[\n \t]*)', re.U | re.I | re.M)
in_word_tag_del = re.compile(r'([A-Za-z;])($e)([A-Za-z&])', re.U | re.I | re.M)
text_tag = re.compile(r'<text\W', re.U | re.I)
closed_text_tag = re.compile(r'</text\W', re.U | re.I)
doc_body_tag = re.compile(r'<docbody', re.U | re.I)
body_tag = re.compile(r'<body\W', re.U | re.I)
div_tag = re.compile(r'<div', re.U | re.I)
para_tag = re.compile(r'<p\W', re.U | re.I)
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
attrib_matcher = re.compile(r'''(\S+)=["']?((?:.(?!["']?\s+(?:\S+)=|[>"']))+.)["']?''', re.U | re.I)
tag_matcher = re.compile(r'<(\w+)[^>]*>', re.U | re.I)
head_self_close_tag = re.compile(r'<head\/>', re.I | re.U)
closed_div_tag = re.compile(r'<\/div', re.I | re.U)
head_tag = re.compile(r'<head', re.U | re.I)
closed_head_tag = re.compile(r'<\/head>', re.U | re.I)
break_apost = re.compile(r'\&apos;', re.U | re.I)

# Entities regexes
entity_regex = [
    re.compile(r'(\&space;)', re.U | re.I),
    re.compile(r'(\&mdash;)', re.U | re.I),
    re.compile(r'(\&nbsp;)', re.U | re.I),
    re.compile(r'(\&para;)', re.U | re.I),
    re.compile(r'(\&sect;)', re.U | re.I),
    re.compile(r'(\&ast;)', re.U | re.I),
    re.compile(r'(\&commat;)', re.U | re.I),
    re.compile(r'(\&ldquo;)', re.U | re.I),
    re.compile(r'(\&laquo;)', re.U | re.I),
    re.compile(r'(\&rdquo;)', re.U | re.I),
    re.compile(r'(\&raquo;)', re.U | re.I),
    re.compile(r'(\&lsquo;)', re.U | re.I),
    re.compile(r'(\&rsquo;)', re.U | re.I),
    re.compile(r'(\&quot;)', re.U | re.I),
    re.compile(r'(\&sup[0-9]*;)', re.U | re.I),
    re.compile(r'(\&mdash;)', re.U | re.I),
    re.compile(r'(\&amp;)', re.U | re.I),
    re.compile(r'(\&deg;)', re.U | re.I),
    re.compile(r'(\&ndash;)', re.U | re.I),
    re.compile(r'(\&copy;)', re.U | re.I),
    re.compile(r'(\&gt;)', re.U | re.I),
    re.compile(r'(\&lt;)', re.U | re.I),
    re.compile(r'(\&frac[0-9]*;)', re.U | re.I),
    re.compile(r'(\&pound;)', re.U | re.I),
    re.compile(r'(\&colon;)', re.U | re.I),
    re.compile(r'(\&hyphen;)', re.U | re.I),
    re.compile(r'(\&dash;)', re.U | re.I),
    re.compile(r'(\&excl;)', re.U | re.I),
    re.compile(r'(\&dagger;)', re.U | re.I),
    re.compile(r'(\&ddagger;)', re.U | re.I),
    re.compile(r'(\&times;)', re.U | re.I),
    re.compile(r'(\&blank;)', re.U | re.I),
    re.compile(r'(\&dollar;)', re.U | re.I),
    re.compile(r'(\&cent;)', re.U | re.I),
    re.compile(r'(\&verbar;)', re.U | re.I),
    re.compile(r'(\&quest;)', re.U | re.I),
    re.compile(r'(\&hellip;)', re.U | re.I),
    re.compile(r'(\&percnt;)', re.U | re.I),
    re.compile(r'(\&middot;)', re.U | re.I),
    re.compile(r'(\&plusmn;)', re.U | re.I),
    re.compile(r'(\&sqrt;)', re.U | re.I),
    re.compile(r'(\&sol;)', re.U | re.I),
    re.compile(r'(\&sdash;)', re.U | re.I),
    re.compile(r'(\&equals;)', re.U | re.I),
    re.compile(r'(\&ornament;)', re.U | re.I),
    re.compile(r'(\&rule;)', re.U | re.I),
    re.compile(r'(\&prime;)', re.U | re.I),
    re.compile(r'(\&rsqb;)', re.U | re.I),
    re.compile(r'(\&lsqb;)', re.U | re.I),
    re.compile(r'(\&punc;)', re.U | re.I),
    re.compile(r'(\&cross;)', re.U | re.I),
    re.compile(r'(\&diamond;)', re.U | re.I),
    re.compile(r'(\&lpunctel;)', re.U | re.I),
    re.compile(r'(\&lsemicol;)', re.U | re.I),
    re.compile(r'(\&plus;)', re.U | re.I),
    re.compile(r'(\&minus;)', re.U | re.I),
    re.compile(r'(\&ounce;)', re.U | re.I),
    re.compile(r'(\&rindx;)', re.U | re.I),
    re.compile(r'(\&lindx;)', re.U | re.I),
    re.compile(r'(\&leaf;)', re.U | re.I),
    re.compile(r'(\&radic;)', re.U | re.I),
    re.compile(r'(\&dram;)', re.U | re.I),
    re.compile(r'(\&sun;)', re.U | re.I),
]

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
