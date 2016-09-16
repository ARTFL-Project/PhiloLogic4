"""This is a port of the PhiloLogic3 parser originally written by Mark Olsen in Perl."""
import os
import re
import string
import sys

from philologic import OHCOVector


DefaultTagToObjMap = {
    "div": "div",
    "div1": "div",
    "div2": "div",
    "div3": "div",
    "hyperdiv": "div",
    "front": "div",
    "note": "div",
    "p": "para",
    "sp": "para",
    "lg": "para",
    "epigraph": "para",
    "argument": "para",
    "postscript": "para",
    "opener": "para",
    "closer": "para",
    "stage": "para",
    "castlist": "para",
    "list": "para",
    "q": "para",
    "add": "para",
    "pb": "page",
    "ref": "ref",
    "l": "line",
    "ab": "line"
}

DefaultMetadataToParse = {
    "div": ["head", "type", "n", "id", "vol"],
    "para": ["who", "resp"], # for <sp> and <add> tags
    "page": ["n", "id", "fac"],
    "ref": ["target", "n", "type"],
    "line": ["n"]
}

DefaultDocXPaths = {
    "author": [
        ".//sourceDesc/bibl/author[@type='marc100']",
        ".//sourceDesc/bibl/author[@type='artfl']",
        ".//sourceDesc/bibl/author",
        ".//titleStmt/author",
        ".//sourceDesc/biblStruct/monogr/author/name",
        ".//sourceDesc/biblFull/titleStmt/author",
        ".//sourceDesc/biblFull/titleStmt/respStmt/name",
        ".//sourceDesc/biblFull/titleStmt/author",
        ".//sourceDesc/bibl/titleStmt/author"
    ],
    "title": [
        ".//sourceDesc/bibl/title[@type='marc245']",
        ".//sourceDesc/bibl/title[@type='artfl']",
        ".//sourceDesc/bibl/title",
        ".//titleStmt/title",
        ".//sourceDesc/bibl/titleStmt/title",
        ".//sourceDesc/biblStruct/monogr/title",
        ".//sourceDesc/biblFull/titleStmt/title"
    ],
    "author_dates": [
        ".//sourceDesc/bibl/author/date",
        ".//titlestmt/author/date"
    ],
    "create_date": [
        ".//profileDesc/creation/date",
        ".//fileDesc/sourceDesc/bibl/imprint/date",
        ".//sourceDesc/biblFull/publicationStmt/date",
        ".//profileDesc/dummy/creation/date",
        ".//fileDesc/sourceDesc/bibl/creation/date"
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
        ".//publicationStmp"
    ],
    "pub_place": [
        ".//sourceDesc/bibl/imprint/pubPlace",
        ".//sourceDesc/biblFull/publicationStmt/pubPlace",
        ".//sourceDesc/biblStruct/monog/imprint/pubPlace",
        ".//sourceDesc/bibl/pubPlace",
        ".//sourceDesc/bibl/publicationStmt/pubPlace"
    ],
    "pub_date": [
        ".//sourceDesc/bibl/imprint/date",
        ".//sourceDesc/biblStruct/monog/imprint/date",
        ".//sourceDesc/biblFull/publicationStmt/date",
        ".//sourceDesc/bibFull/imprint/date",
        ".//sourceDesc/bibl/date",
        ".//text/front/docImprint/acheveImprime"
    ],
    "extent": [
        ".//sourceDesc/bibl/extent",
        ".//sourceDesc/biblStruct/monog//extent",
        ".//sourceDesc/biblFull/extent"
    ],
    "editor": [
        ".//sourceDesc/bibl/editor",
        ".//sourceDesc/biblFull/titleStmt/editor",
        ".//sourceDesc/bibl/title/Stmt/editor"
    ],
    "text_genre": [
        ".//profileDesc/textClass/keywords[@scheme='genre']/term",
        ".//SourceDesc/genre"
    ],
    "keywords": [
        ".//profileDesc/textClass/keywords/list/item"
    ],
    "language": [
        ".//profileDesc/language/language"
    ],
    "notes": [
        ".//fileDesc/notesStmt/note",
        ".//publicationStmt/notesStmt/note"
    ],
    "auth_gender": [
        ".//publicationStmt/notesStmt/note"
    ],
    "collection": [
        ".//seriesStmt/title"
    ],
    "period": [
        ".//profileDesc/textClass/keywords[@scheme='period']/list/item",
        ".//SourceDesc/period",
        ".//sourceDesc/period"
    ],
    "text_form": [
        ".//profileDesc/textClass/keywords[@scheme='form']/term"
    ],
    "structure": [
        ".//SourceDesc/structure",
        ".//sourceDesc/structure"
    ],
    "idno": [
        ".//publicationStmt/idno/",
        ".//seriesStmt/idno/"
    ]
}

TagExceptions = ['<hi[^>]*>',
                 '<emph[^>]*>',
                 '<\/hi>',
                 '<\/emph>',
		         '<orig[^>]*>',
                 '<\/orig>',
		         '<sic[^>]*>',
                 '<\/sic>',
		         '<abbr[^>]*>',
                 '<\/abbr>']

CharsNotToIndex = "\[\{\]\}"


class XMLParser(object):
    """Parses clean or dirty XML."""

    def __init__(self,
                 output,
                 docid,
                 filesize,
                 suppress_tags=[],
                 filtered_words=[],
                 known_metadata=["doc", "div1", "div2", "div3", "para", "sent", "word"],
                 tag_to_obj_map=DefaultTagToObjMap,
                 metadata_to_parse=DefaultMetadataToParse,
                 **parse_options):
        self.types = ["doc", "div1", "div2", "div3", "para", "sent", "word"]
        self.parallel_type = "page"
        self.output = output
        self.docid = docid

        self.tag_to_obj_map = tag_to_obj_map

        self.metadata_to_parse = {}
        for obj in metadata_to_parse:
            self.metadata_to_parse[obj] = set(metadata_to_parse[obj])

        # Initialize an OHCOVector Stack. operations on this stack produce all parser output.
        self.v = OHCOVector.CompoundStack(self.types, self.parallel_type, docid=docid, out=output, ref="ref", line="line")

        self.filesize = filesize
        self.known_metadata = known_metadata

        self.filtered_words = []

        # List of global variables used for the tag handler
        if "token_regex" in parse_options:
            self.token_regex = re.compile(r"(%s)" % parse_options["token_regex"], re.I)
        else:
            self.token_regex = re.compile(r"(%s)" % TokenRegex, re.I)

        if "suppress_tags" in parse_options:
            self.suppress_xpaths = parse_options["suppress_tags"]
        else:
            self.suppress_xpaths = []

        if "break_apost" in parse_options:
            self.break_apost = parse_options["break_apost"]
        else:
            self.break_apost = True

        if "chars_not_to_index" in parse_options:
            self.chars_not_to_index = re.compile(r'%s' % parse_options["chars_not_to_index"], re.I)
        else:
            self.chars_not_to_index = re.compile(r'%s' % CharsNotToIndex, re.I)

        if "break_sent_in_line_group" in parse_options:
            self.break_sent_in_line_group = parse_options["break_sent_in_line_group"]
        else:
            self.break_sent_in_line_group = False

        if "tag_exceptions" in parse_options:
            self.tag_exceptions = parse_options["tag_exceptions"]
        else:
            self.tag_exceptions = TagExceptions

        if "join_hyphen_in_words" in parse_options:
            self.join_hyphen_in_words = parse_options["join_hyphen_in_words"]
        else:
            self.join_hyphen_in_words = True

        if "abbrev_expand" in parse_options:
            self.abbrev_expand = parse_options["abbrev_expand"]
        else:
            self.abbrev_expand = True

        if "long_word_limit" in parse_options:
            self.long_word_limit = parse_options["long_word_limit"]
        else:
            self.long_word_limit = 200

        # Convert SGML ligatures to base characters for indexing, e.g. &oelig; = oe.
        self.flatten_ligatures = True
        self.get_multiple_div_heads = 1  # TODO: remove??
        self.in_the_text = False
        self.in_text_quote = False
        self.in_front_matter = False
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
        self.in_tagged_sentence = False
        self.got_a_div = False
        self.got_a_para = False
        self.context_div_level = 0
        self.current_tag = "doc"
        self.in_a_word_tag = False
        self.in_notes_div = False
        self.current_div1_id = ""
        self.current_div_level = 0
        self.in_seg = False

    def parse(self, input):
        """Top level function for reading a file and printing out the output."""
        self.input = input
        self.content = input.read()
        if div_tag.search(self.content):
            self.got_a_div = True
        if para_tag.search(self.content):
            self.got_a_para = True
        self.cleanup_content()

        # Begin by creating a document level object, just call it "text" for now.
        self.v.push("doc", "text", 0)

        # if the parser was created with known_metadata,
        # we can attach it to the newly created doc object here.
        # you can attach metadata to an object at any time between push() and pull().
        for k, v in self.known_metadata.iteritems():
            self.v["doc"][k] = v

        # Split content into a list on newlines.
        self.content = self.content.split('\n')

        self.bytes_read_in = 0
        self.line_count = 0
        for line in self.content:
            # Let's start indexing words and objects at either the <text
            # of the <docbody tag.  We can add more.

            if text_tag.search(line) or doc_body_tag.search(line) or body_tag.search(line) or closed_head_tag.search(
                    line):
                self.in_the_text = True

            self.line_count += 1

            if line.startswith('<'):
                self.bytes_read_in += len(line)
                # TODO : implement DUMPXPATHS?
                if self.in_the_text:
                    self.tag_handler(line)
            else:
                if line not in self.filtered_words:
                    self.word_handler(line)
                self.bytes_read_in += len(line)

        self.v.pull("doc", self.filesize)

    def cleanup_content(self):
        """Run various clean-ups before parsing."""
        # Replace carriage returns with spaces since they can give us all kinds of difficulties.
        self.content = self.content.replace('\r', ' ')

        # Join hyphens
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
        start_byte = self.bytes_read_in - len(tag)
        try:
            tag_name = tag_matcher.findall(tag)[0]
        except IndexError:
            tag_name = "unparsable_tag"
        if not tag_name.startswith('/'):
            self.current_tag = tag_name

        # print tag_name, start_byte
        # Handle <q> tags
        if text_tag.search(tag) and self.in_text_quote:
            self.in_quote_text_tag = True
        if closed_text_tag.search(tag):
            self.in_quote_text_tag = False
        if quote_tag.search(tag):
            self.in_text_quote = True
        if closed_quote_tag.search(tag):
            self.in_text_quote = False

        # Word tags: store attributes to be attached to the actual word in word_handler
        if self.current_tag == "w":
            self.word_tag_attributes = self.get_attributes(tag)

        # Paragraphs
        elif parag_tag.search(tag) or parag_with_attrib_tag.search(tag):
            do_this_para = True
            if self.in_a_note and not self.in_notes_div:
                do_this_para = False
            if self.no_deeper_objects:
                do_this_para = False
            if do_this_para:
                if self.open_para:  # account for unclosed paragraph tags
                    para_end_byte = self.bytes_read_in - len(tag)
                    self.close_para(para_end_byte)
                self.v.push("para", tag_name, start_byte)
                self.get_object_attributes(tag, tag_name, "para")
                self.open_para = True

        # Notes: treat as para objects and set flag to not set paras in notes.
        elif note_tag.search(tag) and not self.no_deeper_objects:
            if self.open_para:  # account for unclosed paragraph tags
                para_end_byte = self.bytes_read_in - len(tag)
                self.close_para(para_end_byte)
            self.open_div2 = True
            self.v.push("div2", tag_name, start_byte)
            self.get_object_attributes(tag, tag_name, "div2")
            self.in_a_note = True

        # Epigraph: treat as paragraph objects
        elif epigraph_tag.search(tag):
            if self.open_para:  # account for unclosed paragraph tags
                para_end_byte = self.bytes_read_in - len(tag)
                self.close_para(para_end_byte)
            self.open_para = True
            self.v.push("para", tag_name, start_byte)
            self.get_object_attributes(tag, tag_name, "para")
            self.no_deeper_objects = True
        elif closed_epigraph_tag.search(tag):
            self.close_para(self.bytes_read_in)
            self.no_deeper_objects = False
            self.open_para = False

        # LIST: treat as para objects
        elif list_tag.search(tag) and not self.no_deeper_objects:
            if self.open_para:  # account for unclosed paragraph tags
                para_end_byte = self.bytes_read_in - len(tag)
                self.close_para(para_end_byte)
            self.open_para = True
            self.v.push("para", tag_name, start_byte)
            self.get_object_attributes(tag, tag_name, "para")

        # SPEECH BREAKS: treat them as para objects
        elif speaker_tag.search(tag):
            if self.open_para:  # account for unclosed paragraph tags
                para_end_byte = self.bytes_read_in - len(tag)
                self.close_para(para_end_byte)
            self.open_para = True
            self.v.push("para", tag_name, start_byte)
            self.get_object_attributes(tag, tag_name, "para")
            self.no_deeper_objects = True
        elif closed_speaker_tag.search(tag):
            self.close_para(self.bytes_read_in)
            self.no_deeper_objects = False
            self.open_para = False

        # ARGUMENT BREAKS: treat them as para objects
        elif argument_tag.search(tag):
            if self.open_para:  # account for unclosed paragraph tags
                para_end_byte = self.bytes_read_in - len(tag)
                self.close_para(para_end_byte)
            self.open_para = True
            self.v.push("para", tag_name, start_byte)
            self.get_object_attributes(tag, tag_name, "para")
            self.no_deeper_objects = True
        elif closed_argument_tag.search(tag):
            self.close_para(self.bytes_read_in)
            self.no_deeper_objects = False
            self.open_para = False

        # OPENER BREAKS: treat them as para objects
        elif opener_tag.search(tag):
            if self.open_para:  # account for unclosed paragraph tags
                para_end_byte = self.bytes_read_in - len(tag)
                self.close_para(para_end_byte)
            self.open_para = True
            self.v.push("para", tag_name, start_byte)
            self.get_object_attributes(tag, tag_name, "para")
            self.no_deeper_objects = True
        elif closed_opener_tag.search(tag):
            self.close_para(self.bytes_read_in)
            self.no_deeper_objects = False
            self.open_para = False

        # CLOSER BREAKS: treat them as para objects
        elif closer_tag.search(tag):
            if self.open_para:  # account for unclosed paragraph tags
                para_end_byte = self.bytes_read_in - len(tag)
                self.close_para(para_end_byte)
            self.open_para = True
            self.v.push("para", tag_name, start_byte)
            self.get_object_attributes(tag, tag_name, "para")
            self.no_deeper_objects = True
        elif closed_closer_tag.search(tag):
            self.close_para(self.bytes_read_in)
            self.no_deeper_objects = False
            self.open_para = False

        # STAGE DIRECTIONS: treat them as para objects
        # TODO: what to do with stage direction??? deactivated to avoid clashing with <sp> tags
        elif stage_tag.search(tag) and not self.no_deeper_objects:
            if self.open_para:  # account for unclosed paragraph tags
                para_end_byte = self.bytes_read_in - len(tag)
                self.close_para(para_end_byte)
            self.open_para = True
            self.v.push("para", tag_name, start_byte)
            self.get_object_attributes(tag, tag_name, "para")
        elif closed_stage_tag.search(tag):
            self.close_para(self.bytes_read_in)

        # CAST LIST: treat them as para objects
        elif castlist_tag.search(tag):
            if self.open_para:  # account for unclosed paragraph tags
                para_end_byte = self.bytes_read_in - len(tag)
                self.close_para(para_end_byte)
            self.open_para = True
            self.v.push("para", tag_name, start_byte)
            self.get_object_attributes(tag, tag_name, "para")

        # Handle <add> tags as a para.
        elif add_tag.search(tag):
            if self.open_para:  # account for unclosed paragraph tags
                para_end_byte = self.bytes_read_in - len(tag)
                self.close_para(para_end_byte)
            self.open_para = True
            self.v.push("para", tag_name, start_byte)
            self.get_object_attributes(tag, tag_name, "para")
            self.no_deeper_objects = True
        elif tag == "</add>":
            self.close_para(self.bytes_read_in)
            self.no_deeper_objects = False

        # PAGE BREAKS: this updates the currentpagetag or sets it to "na" if not found.
        # TODO: handling of attributes
        elif page_tag.search(tag):
            if self.open_page:
                self.v.pull("page", self.bytes_read_in)
                self.open_page = False
            self.v.push("page", tag_name, start_byte)
            self.get_object_attributes(tag, tag_name, "page")
            try:
                n = self.v["page"]["n"]
                n = n.replace(' ', '_').replace('-', '_').lower()
                if not n:
                    n = "na"
            except KeyError:
                n = "na"
            self.v["page"]["n"] = n
            self.open_page = True

        # LINE GROUP TAGS: treat linegroups same a paragraphs, set or unset the global
        # variable self.in_line_group.
        elif line_group_tag.search(tag) and not self.no_deeper_objects:
            if self.break_sent_in_line_group:
                self.in_line_group = True
            if self.open_para:  # account for unclosed paragraph tags
                para_end_byte = self.bytes_read_in - len(tag)
                self.close_para(para_end_byte)
            self.open_para = True
            self.v.push("para", tag_name, start_byte)
            self.get_object_attributes(tag, tag_name, "para")
        elif closed_line_group.search(tag):
            self.in_line_group = False
            self.close_para(self.bytes_read_in)

        # END LINE TAG: use this to break "sentences" if self.in_line_group.  This is
        # if to set searching in line groups to lines rather than sentences.
        # TODO: not sure I got this right...
        elif line_tag.search(tag):
            if self.in_line_group and self.break_sent_in_line_group:
                self.v.push("sent", tag_name, start_byte)
                self.v.pull("sent", self.bytes_read_in)
            # Create line parallel object
            self.v.push("line", tag_name, start_byte)
            self.get_object_attributes(tag, tag_name, "line")
            self.v["line"].attrib["doc_id"] = self.docid
        elif closed_line_tag.search(tag):
            self.v.pull("line", self.bytes_read_in)

        if ab_tag.search(tag):
            # Create line parallel object
            self.v.push("line", tag_name, start_byte)
            self.get_object_attributes(tag, tag_name, "line")
            self.v["line"].attrib["doc_id"] = self.docid
        elif closed_ab_tag.search(tag):
            self.v.pull("line", self.bytes_read_in)



        # SENTENCE TAG: <s> </s>.  We have never seen a sample of these
        # but let's add the required code to note the beginning of a new
        # sentence and to turn off automatic sentence tagging
        elif sentence_tag.search(tag):
            if self.open_sent or self.in_tagged_sentence:
                self.v.pull("sent", self.bytes_read_in)  # should cache name
            self.v.push("sent", tag_name, start_byte)
            self.in_tagged_sentence = True
            self.open_sent = True
        elif closed_sentence_tag.search(tag):
            self.v.pull("sent", self.bytes_read_in)
            self.in_tagged_sentence = False
            self.open_sent = False

        # TODO: handle docbody

        # FRONT: Treat <front as a <div
        # TODO : test for inner divs as in Philo3???
        elif front_tag.search(tag):
            if self.open_div1:
                self.close_div1(start_byte)
            self.in_front_matter = True
            self.v.push("div1", "front", start_byte)
            self.get_object_attributes(tag, tag_name, "div1")
            self.context_div_level = 1
            self.open_div1 = True
        elif closed_front_tag.search(tag):
            self.in_front_matter = False
            self.context_div_level = 0
            self.close_div1(self.bytes_read_in)

        # BODY TAG: Let's set it as a <div object if we have no divs in the document.
        # These tend to carry on as FRONTMATTER. Don't have to check for lower divs, etc.
        elif body_tag.search(tag) and not self.got_a_div:
            self.v.push("div1", tag_name, start_byte)
            self.current_div1_id = self.v["div1"].id
            self.context_div_level = 1
            self.open_div1 = True
            div_head = self.get_div_head(tag)
            if '[NA]' in div_head or '[na]' in div_head:
                div_head = "Document Body"
            self.v["div1"]["head"] = div_head

        # HyperDiv: This is a Brown WWP construct. It is defined as a place to put
        # a number of different kinds of information which are related to the body
        # of the text but do not appear directly within its flow, for instance footnotes,
        # acrostics, and castlist information which is not printed in the text but
        # is required to provide IDREFs for the who attribute on <speaker>.
        elif hyper_div_tag.search(tag):
            if self.open_div1:
                self.close_div1(start_byte)
            self.context_div_level = 1
            self.open_div1 = True
            self.v.push("div1", tag_name, start_byte)
            self.current_div1_id = self.v["div1"].id
            self.v["div1"]["head"] = "[HyperDiv]"

        # DIV TAGS: set division levels and print out div info. A couple of assumptions:
        # - I assume divs are numbered 1,2,3.
        # - I output <head> info where I find it.  This could also be modified to output
        #   a structured table record with div type, and other attributes, along with
        #   the Philoid and head for searching under document levels.
        elif closed_div_tag.search(tag):
            if "div1" in tag_name:
                if self.in_front_matter:
                    self.v.pull("div2", self.bytes_read_in)
                else:
                    self.v.pull("div1", self.bytes_read_in)
            elif "div2" in tag_name:
                if self.in_front_matter:
                    self.v.pull("div3", self.bytes_read_in)
                else:
                    self.v.pull("div2", self.bytes_read_in)
            elif "div3" in tag_name:
                self.v.pull("div3", self.bytes_read_in)
            self.context_div_level -= 1
            self.no_deeper_objects = False
        elif div_tag.search(tag):
            self.context_div_level += 1
            if self.context_div_level > 3:
                if self.open_div3:
                    self.close_div3(start_byte)
                self.context_div_level = 3
            if self.context_div_level < 1:
                self.context_div_level = 1

            div_level = tag_name[-1]
            if not div_level.isdigit():
                div_level = self.context_div_level
            elif div_level == "0" or int(div_level) > 3:
                div_level = self.context_div_level
            else:
                div_level = int(div_level)
            # <Front is top level div1, so inner divs should be div2s or div3s
            if self.in_front_matter:
                div_level = self.context_div_level
            self.context_div_level = div_level

            # TODO what to do with div0? See philo3???



            # TODO: ignore divs inside of internal text tags.  Setable
            # from configuration.  But we will bump the para and sent args

            if div_level == 1:
                if self.open_div1:
                    self.close_div1(start_byte)
                self.open_div1 = True
                self.v.push("div1", tag_name, start_byte)
                self.current_div1_id = self.v["div1"].id
                self.v["div1"]['head'] = self.get_div_head(tag)
                self.get_object_attributes(tag, tag_name, object_type="div1")
                if "type" in self.v["div1"]:
                    if self.v["div1"]["type"] == "notes":
                        self.in_notes_div = True
                        self.no_deeper_objects = False
            elif div_level == 2:
                if self.open_div2:
                    self.close_div2(start_byte)
                self.open_div2 = True
                self.v.push("div2", tag_name, start_byte)
                self.v["div2"]['head'] = self.get_div_head(tag)
                self.get_object_attributes(tag, tag_name, object_type="div2")
            else:
                if self.open_div3:
                    self.close_div3(start_byte)
                self.open_div3 = True
                self.v.push("div3", tag_name, start_byte)
                self.v["div3"]['head'] = self.get_div_head(tag)
                self.get_object_attributes(tag, tag_name, object_type="div3")

            # TODO: unclear if we need to add EEBO hack when no subdiv objects...

        # We are handling the case of index tags containing attributes which describe the parent div
        # the type attrib has its value in the value attrib
        elif tag_name == "index" and self.context_div_level != 0:
            attrib = dict(self.get_attributes(tag))
            div = "div%d" % self.context_div_level
            if attrib["type"] in self.metadata_to_parse["div"]:
                self.v[div].attrib[attrib["type"]] = attrib["value"]

        elif tag_name == "ref":
            self.v.push("ref", tag_name, start_byte)
            self.get_object_attributes(tag, tag_name, "ref")
            self.v["ref"].attrib["parent"] = " ".join([str(i) for i in self.current_div1_id])
            self.v.pull("ref", self.bytes_read_in)

    def word_handler(self, words):
        """
        Word handler. It takes an artbitrary string or words between two tags and
        splits them into words. It also identifies sentence breaks.  I am not checking for existing sentence
        tags, but could and conditionalize it. Also note that it does not check for
        sentences inside of linegroups ... which are typically broken on lines.
        I am not currently handling ";" at the end of words because of confusion with
        character ents. Easily fixed.
        """
        # We don't like many character entities, so let's change them
        # into spaces to get a clean break.
        if char_ents.search(words):
            words = self.clear_char_ents(words)

        # TODO: Now, we also know that there are Unicode characters which
        # we normally want to break words.  Often, these are Microsoft characters
        # like the curly quotes. These are set in textload.cfg
        # in @UnicodeWordBreakers.

        # TODO: Now, here's something you did not think of: Brown WWP: M&sup-r;
        # You are going to split words, on hyphens just below.  That would
        # be a mess.  So a little exception handler which we will convert
        # to the supp(.) for indexing.

        # we're splitting the line of words into distinct words
        # separated by "\n"
        words = self.token_regex.sub(r'\n\1\n', words)

        if self.break_apost:
            words = words.replace("'", "\n'\n")

        words = newline_shortener.sub(r'\n', words)

        current_pos = self.bytes_read_in
        count = 0
        word_list = words.split('\n')
        last_word = ""
        next_word = ""
        if self.in_the_text:
            for word in word_list:
                # print word, current_pos - len(word)
                word_length = len(word)
                try:
                    next_word = word_list[count + 1]
                except IndexError:
                    pass
                count += 1

                # Keep track of your bytes since this is where you are getting
                # the byte offsets for words.
                current_pos += word_length

                # Do we have a word? At least one of these characters.
                if check_if_char_word.search(word):
                    last_word = word
                    word_pos = current_pos - len(word)

                    # Set your byte position now, since you will be modifying the
                    # word you are sending to the index after this.
                    start_byte = word_pos

                    if "&" in word:
                        # Convert ents to utf-8
                        word = self.latin1_ents_to_utf8(word)
                        # Convert other ents to things....
                        word = self.convert_other_ents(word)

                    # You may have some semi-colons...
                    if word[-1] == ";":
                        if "&" in word:
                            pass  # TODO
                        else:
                            word = word[:-1]

                    # Get rid of certain characters that don't break words, but don't index.
                    # These are defined in a compiled regex below: chars_not_to_index
                    word = chars_not_to_index.sub('', word)

                    # TODO: Call a function to distinguish between words beginning with an
                    # upper case and lower case character.  This USED to be a proper
                    # name split in ARTFL, but we don't see many databases with proper
                    # names tagged.

                    # Switch everything to lower case
                    word = word.decode('utf8', 'ignore').lower().encode('utf8')

                    # TODO: If you have tag exemptions and you have some of the replacement
                    # characters "_", then delete them from the index entry.  I've put
                    # in both options, just in case.  I'm on the fence about this at the
                    # moment since I have "_" in characters to match above.

                    # Check to see if the word is longer than we want.  More than 235
                    # characters appear to cause problems in the indexer.
                    # TODO: make this limit configurable?
                    if len(word) > 235:
                        print >> sys.stderr, "Long word: %s" % word
                        print >> sys.stderr, "Truncating for index..."
                        word = word[:235]

                    word = self.remove_control_chars(word)
                    word = word.strip().replace("_", "")
                    if len(word):
                        self.v.push("word", word, word_pos)
                        if self.current_tag == "w":
                            for attrib, value in self.word_tag_attributes:
                                self.v["word"][attrib] = value
                        self.v.pull("word", current_pos)

                # Sentence break handler
                elif not self.in_line_group and not self.in_tagged_sentence:
                    is_sent = False

                    # Always break on ! and ?
                    # TODO: why test if word > 2 in p3?
                    if "!" in word or "?" in word:
                        is_sent = True

                    # Periods are messy. Let's try by length of previous word and
                    # capital letters to avoid hitting abbreviations.
                    elif '.' in word:
                        is_sent = True
                        if len(last_word.decode('utf8', 'ignore')) < 3:
                            if cap_char_or_num.search(last_word):
                                is_sent = False

                        # Periods in numbers don't break sentences.
                        if next_word.islower() or next_word.isdigit():
                            is_sent = False

                    if is_sent:
                        # a little hack--we don't know the punctuation mark that will end a sentence
                        # until we encounter it--so instead, we let the push on "word" create a
                        # implicit philo_virtual sentence, then change its name once we actually encounter
                        # the punctuation token.
                        if "sent" not in self.v:
                            self.v.push("sent", ".", current_pos)
                        self.v[
                            "sent"].name = "."  # TODO: evaluate if this is right: avoid unwanted chars such tabs in ASP
                        self.v.pull("sent", current_pos + len(word))

    def close_sent(self, end_byte):
        """Close sentence objects."""
        self.v.pull("sent", end_byte)
        self.open_sent = False

    def close_para(self, end_byte):
        """Close paragraph objects."""
        if self.open_sent:
            self.close_sent(end_byte)
        self.v.pull("para", end_byte)
        self.open_para = False

    def close_div3(self, end_byte):
        """Close div3 objects."""
        if self.open_para:
            self.close_para(end_byte)
        self.v.pull("div3", end_byte)
        self.open_div3 = False

    def close_div2(self, end_byte):
        """Close div2 objects."""
        if self.open_div3:
            self.close_div3(end_byte)
        self.v.pull("div2", end_byte)
        self.open_div1 = False

    def close_div1(self, end_byte):
        """Close div1 objects."""
        if self.open_div2:
            self.close_div2(end_byte)
        self.v.pull("div1", end_byte)
        self.open_div1 = False

    def camel_case_to_snake_case(self, word):
        word = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', word)
        word = re.sub('([a-z0-9])([A-Z])', r'\1_\2', word).lower()
        return word

    def get_attributes(self, tag):
        """Find all attributes for any given tag."""
        attribs = []
        for attrib, value in attrib_matcher.findall(tag):
            # Replace ":" with "_" for attribute nanames since they are illegal in SQLite
            attrib = attrib.replace(':', "_")
            # Because of some bug in the attrib regex, single char values keep the initial quote
            if value.startswith('"'):
                value = value[1:]
            value = self.remove_control_chars(value)
            value = ending_punctuation.sub("", value.strip())
            attribs.append((attrib, value))
        return attribs

    def get_object_attributes(self, tag, tag_name, object_type):
        """Get all attributes for any given tag and attach metadata to element."""
        try:
            text_object = self.tag_to_obj_map[tag_name.lower()]
            retrieve_attrib = True
        except KeyError:
            retrieve_attrib = False
        if retrieve_attrib:
            for attrib, value in self.get_attributes(tag):
                attrib = self.camel_case_to_snake_case(attrib)
                if attrib in self.metadata_to_parse[text_object]:
                    self.v[object_type][attrib] = value

    def get_div_head(self, tag):
        """Get div head."""
        get_head_count = self.get_multiple_div_heads
        read_more = False
        look_ahead = self.line_count
        overflow_trap = 0
        div_head = ""
        while not read_more:
            look_ahead += 1
            try:
                next_line = self.content[look_ahead]
            except IndexError:
                break
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
                            get_head_count -= 1
                    elif overflow_trap > 50:  # Overflow trap in case you miss </head
                        read_more = False
                    else:
                        div_head += next_line
        if div_head:
            div_head = self.clear_char_ents(div_head)
            div_head = self.latin1_ents_to_utf8(div_head)
            div_head = self.convert_other_ents(div_head)
            div_head = re.sub(r'\n?<[^>]*>\n?', '', div_head)
            div_head = div_head.replace('_', '')
            div_head = div_head.replace('\t', '')
            div_head = ' '.join(div_head.split())  # remove double or more spaces
            div_head = div_head.replace('[', '').replace(']', '')
            div_head = div_head.replace('"', '')
            div_head = div_head.strip()
        elif "type=" in tag:
            try:
                div_head = type_attrib.findall(tag)[0]
            except IndexError:
                pass

        if not div_head:
            div_head = "[NA]"

        # TODO: evaluate need for below...
        if div_head == "[>]" or div_head == "[<]":
            div_head == "[NA]"

        div_head = self.remove_control_chars(div_head)
        return div_head

    def clear_char_ents(self, text):
        """Replaces a selected set of SGML character ents with spaces in order to keep the byte count right."""
        # We would want to read a list of character ents that should NOT be considered
        # valid for including in words or, more likely, a list of VALID characters from a general table.
        if self.break_apost:
            try:
                text = apost_ent.sub(lambda match: "," + " " * len(match.group(1) - 1), text)
            except IndexError:
                pass
        for regex in entity_regex:
            try:
                text = regex.sub(lambda match: " " * len(match.group(1)), text)
            except IndexError:
                pass
        return text

    def latin1_ents_to_utf8(self, text):
        """Converts ISO-LATIN-1 character entities in index words to UTF-8
        for standard word index search consistency. This is for SGML data sets
        and XML that have character ents rather than UTF-8 characters."""
        if self.flatten_ligatures:
            text = text.replace('&AElig;', '\xc3\x86')
            text = text.replace('&szlig;', '\xc3\x9F')
            text = text.replace('&aelig;', '\xc3\xA6')
        text = text.replace('&Agrave;', '\xc3\x80')
        text = text.replace('&Aacute;', '\xc3\x81')
        text = text.replace('&Acirc;', '\xc3\x82')
        text = text.replace('&Atilde;', '\xc3\x83')
        text = text.replace('&Auml;', '\xc3\x84')
        text = text.replace('&Aring;', '\xc3\x85')
        text = text.replace('&Ccedil;', '\xc3\x87')
        text = text.replace('&Egrave;', '\xc3\x88')
        text = text.replace('&Eacute;', '\xc3\x89')
        text = text.replace('&Ecirc;', '\xc3\x8A')
        text = text.replace('&Euml;', '\xc3\x8B')
        text = text.replace('&Igrave;', '\xc3\x8C')
        text = text.replace('&Iacute;', '\xc3\x8D')
        text = text.replace('&Icirc;', '\xc3\x8E')
        text = text.replace('&Iuml;', '\xc3\x8F')
        text = text.replace('&ETH;', '\xc3\x90')
        text = text.replace('&Ntilde;', '\xc3\x91')
        text = text.replace('&Ograve;', '\xc3\x92')
        text = text.replace('&Oacute;', '\xc3\x93')
        text = text.replace('&Ocirc;', '\xc3\x94')
        text = text.replace('&Otilde;', '\xc3\x95')
        text = text.replace('&Ouml;', '\xc3\x96')
        text = text.replace('&#215;', '\xc3\x97')  # MULTIPLICATION SIGN
        text = text.replace('&Oslash;', '\xc3\x98')
        text = text.replace('&Ugrave;', '\xc3\x99')
        text = text.replace('&Uacute;', '\xc3\x9A')
        text = text.replace('&Ucirc;', '\xc3\x9B')
        text = text.replace('&Uuml;', '\xc3\x9C')
        text = text.replace('&Yacute;', '\xc3\x9D')
        text = text.replace('&THORN;', '\xc3\x9E')
        text = text.replace('&agrave;', '\xc3\xA0')
        text = text.replace('&aacute;', '\xc3\xA1')
        text = text.replace('&acirc;', '\xc3\xA2')
        text = text.replace('&atilde;', '\xc3\xA3')
        text = text.replace('&auml;', '\xc3\xA4')
        text = text.replace('&aring;', '\xc3\xA5')
        text = text.replace('&ccedil;', '\xc3\xA7')
        text = text.replace('&egrave;', '\xc3\xA8')
        text = text.replace('&eacute;', '\xc3\xA9')
        text = text.replace('&ecirc;', '\xc3\xAA')
        text = text.replace('&euml;', '\xc3\xAB')
        text = text.replace('&igrave;', '\xc3\xAC')
        text = text.replace('&iacute;', '\xc3\xAD')
        text = text.replace('&icirc;', '\xc3\xAE')
        text = text.replace('&iuml;', '\xc3\xAF')
        text = text.replace('&eth;', '\xc3\xB0')
        text = text.replace('&ntilde;', '\xc3\xB1')
        text = text.replace('&ograve;', '\xc3\xB2')
        text = text.replace('&oacute;', '\xc3\xB3')
        text = text.replace('&ocirc;', '\xc3\xB4')
        text = text.replace('&otilde;', '\xc3\xB5')
        text = text.replace('&ouml;', '\xc3\xB6')
        text = text.replace('&#247;', '\xc3\xB7')  # DIVISION SIGN
        text = text.replace('&oslash;', '\xc3\xB8')
        text = text.replace('&ugrave;', '\xc3\xB9')
        text = text.replace('&uacute;', '\xc3\xBA')
        text = text.replace('&ucirc;', '\xc3\xBB')
        text = text.replace('&uuml;', '\xc3\xBC')
        text = text.replace('&yacute;', '\xc3\xBD')
        text = text.replace('&thorn;', '\xc3\xBE')
        text = text.replace('&yuml;', '\xc3\xBF')

        # Greek Entities for HTML4 and Chadwock Healey -- Charles Cooney
        text = text.replace('&agr;', '\xce\xb1')
        text = text.replace('&alpha;', '\xce\xb1')
        text = text.replace('&bgr;', '\xce\xb2')
        text = text.replace('&beta;', '\xce\xb2')
        text = text.replace('&ggr;', '\xce\xb3')
        text = text.replace('&gamma;', '\xce\xb3')
        text = text.replace('&dgr;', '\xce\xb4')
        text = text.replace('&delta;', '\xce\xb4')
        text = text.replace('&egr;', '\xce\xb5')
        text = text.replace('&epsilon;', '\xce\xb5')
        text = text.replace('&zgr;', '\xce\xb6')
        text = text.replace('&zeta;', '\xce\xb6')
        text = text.replace('&eegr;', '\xce\xb7')
        text = text.replace('&eta;', '\xce\xb7')
        text = text.replace('&thgr;', '\xce\xb8')
        text = text.replace('&theta;', '\xce\xb8')
        text = text.replace('&igr;', '\xce\xb9')
        text = text.replace('&iota;', '\xce\xb9')
        text = text.replace('&kgr;', '\xce\xba')
        text = text.replace('&kappa;', '\xce\xba')
        text = text.replace('&lgr;', '\xce\xbb')
        text = text.replace('&lambda;', '\xce\xbb')
        text = text.replace('&mgr;', '\xce\xbc')
        text = text.replace('&mu;', '\xce\xbc')
        text = text.replace('&ngr;', '\xce\xbd')
        text = text.replace('&nu;', '\xce\xbd')
        text = text.replace('&xgr;', '\xce\xbe')
        text = text.replace('&xi;', '\xce\xbe')
        text = text.replace('&ogr;', '\xce\xbf')
        text = text.replace('&omicron;', '\xce\xbf')
        text = text.replace('&pgr;', '\xcf\x80')
        text = text.replace('&pi;', '\xcf\x80')
        text = text.replace('&rgr;', '\xcf\x81')
        text = text.replace('&rho;', '\xcf\x81')
        text = text.replace('&sfgr;', '\xcf\x82')
        text = text.replace('&sigmaf;', '\xcf\x82')
        text = text.replace('&sgr;', '\xcf\x83')
        text = text.replace('&sigma;', '\xcf\x83')
        text = text.replace('&tgr;', '\xcf\x84')
        text = text.replace('&tau;', '\xcf\x84')
        text = text.replace('&ugr;', '\xcf\x85')
        text = text.replace('&upsilon;', '\xcf\x85')
        text = text.replace('&phgr;', '\xcf\x86')
        text = text.replace('&phi;', '\xcf\x86')
        text = text.replace('&khgr;', '\xcf\x87')
        text = text.replace('&chi;', '\xcf\x87')
        text = text.replace('&psgr;', '\xcf\x88')
        text = text.replace('&psi;', '\xcf\x88')
        text = text.replace('&ohgr;', '\xcf\x89')
        text = text.replace('&omega;', '\xcf\x89')
        text = text.replace('&Agr;', '\xce\x91')
        text = text.replace('&Alpha;', '\xce\x91')
        text = text.replace('&Bgr;', '\xce\x92')
        text = text.replace('&Beta;', '\xce\x92')
        text = text.replace('&Ggr;', '\xce\x93')
        text = text.replace('&Gamma;', '\xce\x93')
        text = text.replace('&Dgr;', '\xce\x94')
        text = text.replace('&Delta;', '\xce\x94')
        text = text.replace('&Egr;', '\xce\x95')
        text = text.replace('&Epsilon;', '\xce\x95')
        text = text.replace('&Zgr;', '\xce\x96')
        text = text.replace('&Zeta;', '\xce\x96')
        text = text.replace('&EEgr;', '\xce\x97')
        text = text.replace('&Eta;', '\xce\x97')
        text = text.replace('&THgr;', '\xce\x98')
        text = text.replace('&Theta;', '\xce\x98')
        text = text.replace('&Igr;', '\xce\x99')
        text = text.replace('&Iota;', '\xce\x99')
        text = text.replace('&Kgr;', '\xce\x9a')
        text = text.replace('&Kappa;', '\xce\x9a')
        text = text.replace('&Lgr;', '\xce\x9b')
        text = text.replace('&Lambda;', '\xce\x9b')
        text = text.replace('&Mgr;', '\xce\x9c')
        text = text.replace('&Mu;', '\xce\x9c')
        text = text.replace('&Ngr;', '\xce\x9d')
        text = text.replace('&Nu;', '\xce\x9d')
        text = text.replace('&Xgr;', '\xce\x9e')
        text = text.replace('&Xi;', '\xce\x9e')
        text = text.replace('&Ogr;', '\xce\x9f')
        text = text.replace('&Omicron;', '\xce\x9f')
        text = text.replace('&Pgr;', '\xce\xa0')
        text = text.replace('&Pi;', '\xce\xa0')
        text = text.replace('&Rgr;', '\xce\xa1')
        text = text.replace('&Rho;', '\xce\xa1')
        text = text.replace('&Sgr;', '\xce\xa3')
        text = text.replace('&Sigma;', '\xce\xa3')
        text = text.replace('&Tgr;', '\xce\xa4')
        text = text.replace('&Tau;', '\xce\xa4')
        text = text.replace('&Ugr;', '\xce\xa5')
        text = text.replace('&Upsilon;', '\xce\xa5')
        text = text.replace('&PHgr;', '\xce\xa6')
        text = text.replace('&Phi;', '\xce\xa6')
        text = text.replace('&KHgr;', '\xce\xa7')
        text = text.replace('&Chi;', '\xce\xa7')
        text = text.replace('&PSgr;', '\xce\xa8')
        text = text.replace('&Psi;', '\xce\xa8')
        text = text.replace('&OHgr;', '\xce\xa9')
        text = text.replace('&Omega;', '\xce\xa9')
        return text

    def convert_other_ents(self, text):
        """ handles character entities in index words.
        There should not be many of these."""
        text = text.replace('&apos;', "'")
        text = text.replace('&s;', 's')
        text = macr_ent.sub(r'\1', text)
        text = inverted_ent.sub(r'\1', text)
        text = supp_ent.sub(r'\1', text)
        if self.flatten_ligatures:
            text = ligatures_ent.sub(r'\1', text)
        return text

    def remove_control_chars(self, text):
        return control_char_re.sub('', text.decode('utf8', 'ignore')).encode('utf8')


TokenRegex = "[\&A-Za-z0-9\177-\377][\&A-Za-z0-9\177-\377\_\';]*"

# Pre-compiled regexes used for parsing
join_hyphen_with_lb = re.compile(r'(\&shy;[\n \t]*<lb\/>)', re.I | re.M)
join_hyphen = re.compile(r'(\&shy;[\n \t]*)', re.I | re.M)
in_word_tag_del = re.compile(r'([A-Za-z;])($e)([A-Za-z&])', re.I | re.M)
text_tag = re.compile(r'<text\W', re.I)
closed_text_tag = re.compile(r'</text\W', re.I)
doc_body_tag = re.compile(r'<docbody', re.I)
body_tag = re.compile(r'<body\W', re.I)
div_tag = re.compile(r'<div', re.I)
closed_div_tag = re.compile(r'<\/div', re.I)
para_tag = re.compile(r'<p\W', re.I)
quote_tag = re.compile(r'<q[ >]', re.I)
closed_quote_tag = re.compile(r'</q>', re.I)
parag_tag = re.compile(r'<p>', re.I)
parag_with_attrib_tag = re.compile(r'<p ', re.I)
closed_para_tag = re.compile(r'</p>', re.I)
note_tag = re.compile(r'<note\W', re.I)
closed_note_tag = re.compile(r'</note>', re.I)
epigraph_tag = re.compile(r'<epigraph\W', re.I)
closed_epigraph_tag = re.compile(r'</epigraph>', re.I)
list_tag = re.compile(r'<list\W', re.I)
closed_list_tag = re.compile(r'</list>', re.I)
speaker_tag = re.compile(r'<sp\W', re.I)
closed_speaker_tag = re.compile(r'</sp>', re.I)
argument_tag = re.compile(r'<argument\W', re.I)
closed_argument_tag = re.compile(r'</argument>', re.I)
opener_tag = re.compile(r'<opener\W', re.I)
closed_opener_tag = re.compile(r'</opener\W', re.I)
closer_tag = re.compile(r'<closer\W', re.I)
closed_closer_tag = re.compile(r'</closer\W', re.I)
stage_tag = re.compile(r'<stage\W', re.I)
closed_stage_tag = re.compile(r'</stage\W', re.I)
castlist_tag = re.compile(r'<castlist\W', re.I)
closed_castlist_tag = re.compile(r'</castlist\W', re.I)
page_tag = re.compile(r'<pb\W', re.I)
n_attribute = re.compile(r'n="([^"]*)', re.I)
line_group_tag = re.compile(r'<lg\W', re.I)
closed_line_group = re.compile(r'</lg\W', re.I)
line_tag = re.compile(r'<l\W', re.I)
ab_tag = re.compile(r'<ab\W', re.I)
closed_line_tag = re.compile(r'</l\W', re.I)
closed_ab_tag = re.compile(r'</ab\W', re.I)
sentence_tag = re.compile(r'<s\W', re.I)
closed_sentence_tag = re.compile(r'</s\W', re.I)
front_tag = re.compile(r'<front\W', re.I)
closed_front_tag = re.compile(r'</front\W', re.I)
attrib_matcher = re.compile(r'''(\S+)=["']?((?:.(?!["']?\s+(?:\S+)=|[>"']))+.)["']?''', re.I)
tag_matcher = re.compile(r'<(\/?\w+)[^>]*>?', re.I)
head_self_close_tag = re.compile(r'<head\/>', re.I)
closed_div_tag = re.compile(r'<\/div', re.I)
head_tag = re.compile(r'<head', re.I)
closed_head_tag = re.compile(r'<\/head>', re.I)
apost_ent = re.compile(r'\&apos;', re.I)
macr_ent = re.compile(r'\&([A-Za-z])macr;', re.I)
inverted_ent = re.compile(r'\&inverted([a-zA-Z0-9]);', re.I)
supp_ent = re.compile(r'&supp([a-z0-9]);', re.I)
ligatures_ent = re.compile(r'\&([A-Za-z][A-Za-z])lig;', re.I)
type_attrib = re.compile(r'type="([^"]*)"', re.I)
hyper_div_tag = re.compile(r'<hyperdiv\W', re.I)
div_num_tag = re.compile(r'<div(.)', re.I)
char_ents = re.compile(r'\&[a-zA-Z0-9\#][a-zA-Z0-9]*;', re.I)
newline_shortener = re.compile(r'\n\n*')
check_if_char_word = re.compile(r'[A-Za-z0-9\177-\377]', re.I)
chars_not_to_index = re.compile(r'\[\{\]\}', re.I)
cap_char_or_num = re.compile(r'[A-Z0-9]')  # Capitals
ending_punctuation = re.compile(r'[%s]$' % string.punctuation)
add_tag = re.compile(r'<add\W', re.I)
seg_attrib = re.compile(r'<seg \w+=', re.I)

## Build a list of control characters to remove
## http://stackoverflow.com/questions/92438/stripping-non-printable-characters-from-a-string-in-python/93029#93029
tab_newline = re.compile(r'[\n|\t]')
control_chars = ''.join(
    [i for i in map(lambda x: unichr(x).encode('utf8'), range(0, 32) + range(127, 160)) if not tab_newline.search(i)])
control_char_re = re.compile(r'[%s]' % re.escape(control_chars))

# Entities regexes
entity_regex = [
    re.compile(r'(\&space;)', re.I),
    re.compile(r'(\&mdash;)', re.I),
    re.compile(r'(\&nbsp;)', re.I),
    re.compile(r'(\&para;)', re.I),
    re.compile(r'(\&sect;)', re.I),
    re.compile(r'(\&ast;)', re.I),
    re.compile(r'(\&commat;)', re.I),
    re.compile(r'(\&ldquo;)', re.I),
    re.compile(r'(\&laquo;)', re.I),
    re.compile(r'(\&rdquo;)', re.I),
    re.compile(r'(\&raquo;)', re.I),
    re.compile(r'(\&lsquo;)', re.I),
    re.compile(r'(\&rsquo;)', re.I),
    re.compile(r'(\&quot;)', re.I),
    re.compile(r'(\&sup[0-9]*;)', re.I),
    re.compile(r'(\&mdash;)', re.I),
    re.compile(r'(\&amp;)', re.I),
    re.compile(r'(\&deg;)', re.I),
    re.compile(r'(\&ndash;)', re.I),
    re.compile(r'(\&copy;)', re.I),
    re.compile(r'(\&gt;)', re.I),
    re.compile(r'(\&lt;)', re.I),
    re.compile(r'(\&frac[0-9]*;)', re.I),
    re.compile(r'(\&pound;)', re.I),
    re.compile(r'(\&colon;)', re.I),
    re.compile(r'(\&hyphen;)', re.I),
    re.compile(r'(\&dash;)', re.I),
    re.compile(r'(\&excl;)', re.I),
    re.compile(r'(\&dagger;)', re.I),
    re.compile(r'(\&ddagger;)', re.I),
    re.compile(r'(\&times;)', re.I),
    re.compile(r'(\&blank;)', re.I),
    re.compile(r'(\&dollar;)', re.I),
    re.compile(r'(\&cent;)', re.I),
    re.compile(r'(\&verbar;)', re.I),
    re.compile(r'(\&quest;)', re.I),
    re.compile(r'(\&hellip;)', re.I),
    re.compile(r'(\&percnt;)', re.I),
    re.compile(r'(\&middot;)', re.I),
    re.compile(r'(\&plusmn;)', re.I),
    re.compile(r'(\&sqrt;)', re.I),
    re.compile(r'(\&sol;)', re.I),
    re.compile(r'(\&sdash;)', re.I),
    re.compile(r'(\&equals;)', re.I),
    re.compile(r'(\&ornament;)', re.I),
    re.compile(r'(\&rule;)', re.I),
    re.compile(r'(\&prime;)', re.I),
    re.compile(r'(\&rsqb;)', re.I),
    re.compile(r'(\&lsqb;)', re.I),
    re.compile(r'(\&punc;)', re.I),
    re.compile(r'(\&cross;)', re.I),
    re.compile(r'(\&diamond;)', re.I),
    re.compile(r'(\&lpunctel;)', re.I),
    re.compile(r'(\&lsemicol;)', re.I),
    re.compile(r'(\&plus;)', re.I),
    re.compile(r'(\&minus;)', re.I),
    re.compile(r'(\&ounce;)', re.I),
    re.compile(r'(\&rindx;)', re.I),
    re.compile(r'(\&lindx;)', re.I),
    re.compile(r'(\&leaf;)', re.I),
    re.compile(r'(\&radic;)', re.I),
    re.compile(r'(\&dram;)', re.I),
    re.compile(r'(\&sun;)', re.I),
]

if __name__ == "__main__":
    for docid, fn in enumerate(sys.argv[1:], 1):
        print >> sys.stderr, docid, fn
        size = os.path.getsize(fn)
        fh = open(fn)
        parser = XMLParser(sys.stdout, docid, size, known_metadata={"filename": fn}, tag_to_obj_map=DefaultTagToObjMap,
                           metadata_to_parse=DefaultMetadataToParse)
        parser.parse(fh)
