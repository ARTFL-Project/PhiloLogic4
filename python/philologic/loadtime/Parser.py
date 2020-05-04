#!/usr/bin/env python3
"""PhiloLogic4 main parser"""

import os
import re
import string
import sys

from philologic.loadtime.OHCOVector import CompoundStack
from philologic.utils import convert_entities
from collections import deque

DEFAULT_TAG_TO_OBJ_MAP = {
    "div": "div",
    "div1": "div",
    "div2": "div",
    "div3": "div",
    "hyperdiv": "div",
    "front": "div",
    "note": "para",
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
    "graphic": "graphic",
    "l": "line",
    "ab": "line",
}

DEFAULT_METADATA_TO_PARSE = {
    "div": ["head", "type", "n", "id", "vol"],
    "para": ["who", "resp", "id"],  # for <sp> and <add> tags
    "page": ["n", "id", "facs"],
    "ref": ["target", "n", "type"],
    "graphic": ["facs"],
    "line": ["n", "id"],
}

DEFAULT_DOC_XPATHS = {
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
    "author_dates": [".//sourceDesc/bibl/author/date", ".//titlestmt/author/date"],
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
    "extent": [".//sourceDesc/bibl/extent", ".//sourceDesc/biblStruct/monog//extent", ".//sourceDesc/biblFull/extent"],
    "editor": [
        ".//sourceDesc/bibl/editor",
        ".//sourceDesc/biblFull/titleStmt/editor",
        ".//sourceDesc/bibl/title/Stmt/editor",
    ],
    "text_genre": [".//profileDesc/textClass/keywords[@scheme='genre']/term", ".//SourceDesc/genre"],
    "keywords": [".//profileDesc/textClass/keywords/list/item"],
    "language": [".//profileDesc/language/language"],
    "notes": [".//fileDesc/notesStmt/note", ".//publicationStmt/notesStmt/note"],
    "auth_gender": [".//publicationStmt/notesStmt/note"],
    "collection": [".//seriesStmt/title"],
    "period": [
        ".//profileDesc/textClass/keywords[@scheme='period']/list/item",
        ".//SourceDesc/period",
        ".//sourceDesc/period",
    ],
    "text_form": [".//profileDesc/textClass/keywords[@scheme='form']/term"],
    "structure": [".//SourceDesc/structure", ".//sourceDesc/structure"],
    "idno": [".//publicationStmt/idno/", ".//seriesStmt/idno/"],
}

TAG_EXCEPTIONS = [
    r"<hi[^>]*>",
    r"<emph[^>]*>",
    r"<\/hi>",
    r"<\/emph>",
    r"<orig[^>]*>",
    r"<\/orig>",
    r"<sic[^>]*>",
    r"<\/sic>",
    r"<abbr[^>]*>",
    r"<\/abbr>",
    r"<i>",
    r"</i>",
    r"<sup>",
    r"</sup>",
]

TOKEN_REGEX = r"\w+|[&\w;]+"

PUNCTUATION = r"""[;,:=+()"]"""

CHARS_NOT_TO_INDEX = r"\[\{\]\}"

UNICODE_WORD_BREAKERS = [
    b"\xe2\x80\x93",  # U+2013 &ndash; EN DASH
    b"\xe2\x80\x94",  # U+2014 &mdash; EM DASH
    b"\xc2\xab",  # &laquo;
    b"\xc2\xbb",  # &raquo;
    b"\xef\xbc\x89",  # fullwidth right parenthesis
    b"\xef\xbc\x88",  # fullwidth left parenthesis
    b"\xe2\x80\x90",  # U+2010 hyphen for greek stuff
    b"\xce\x87",  # U+00B7 ano teleia
    b"\xe2\x80\xa0",  # U+2020 dagger
    b"\xe2\x80\x98",  # U+2018 &lsquo; LEFT SINGLE QUOTATION
    b"\xe2\x80\x99",  # U+2019 &rsquo; RIGHT SINGLE QUOTATION
    b"\xe2\x80\x9c",  # U+201C &ldquo; LEFT DOUBLE QUOTATION
    b"\xe2\x80\x9d",  # U+201D &rdquo; RIGHT DOUBLE QUOTATION
    b"\xe2\x80\xb9",  # U+2039 &lsaquo; SINGLE LEFT-POINTING ANGLE QUOTATION
    b"\xe2\x80\xba",  # U+203A &rsaquo; SINGLE RIGHT-POINTING ANGLE QUOTATION
    b"\xe2\x80\xa6",  # U+2026 &hellip; HORIZONTAL ELLIPSIS
]


# Pre-compiled regexes used for parsing
join_hyphen_with_lb = re.compile(r"(\&shy;[\n \t]*<lb\/>)", re.I | re.M)
join_hyphen = re.compile(r"(\&shy;[\n \t]*)", re.I | re.M)
text_tag = re.compile(r"<text\W", re.I)
closed_text_tag = re.compile(r"</text\W", re.I)
doc_body_tag = re.compile(r"<docbody", re.I)
body_tag = re.compile(r"<body\W", re.I)
div_tag = re.compile(r"<div", re.I)
closed_div_tag = re.compile(r"<\/div", re.I)
para_tag = re.compile(r"<p\W", re.I)
quote_tag = re.compile(r"<q[ >]", re.I)
closed_quote_tag = re.compile(r"</q>", re.I)
parag_tag = re.compile(r"<p>", re.I)
parag_with_attrib_tag = re.compile(r"<p ", re.I)
closed_para_tag = re.compile(r"</p>", re.I)
note_tag = re.compile(r"<note\W", re.I)
closed_note_tag = re.compile(r"</note>", re.I)
epigraph_tag = re.compile(r"<epigraph\W", re.I)
closed_epigraph_tag = re.compile(r"</epigraph>", re.I)
list_tag = re.compile(r"<list\W", re.I)
closed_list_tag = re.compile(r"</list>", re.I)
speaker_tag = re.compile(r"<sp\W", re.I)
closed_speaker_tag = re.compile(r"</sp>", re.I)
argument_tag = re.compile(r"<argument\W", re.I)
closed_argument_tag = re.compile(r"</argument>", re.I)
opener_tag = re.compile(r"<opener\W", re.I)
closed_opener_tag = re.compile(r"</opener\W", re.I)
closer_tag = re.compile(r"<closer\W", re.I)
closed_closer_tag = re.compile(r"</closer\W", re.I)
stage_tag = re.compile(r"<stage\W", re.I)
closed_stage_tag = re.compile(r"</stage\W", re.I)
castlist_tag = re.compile(r"<castlist\W", re.I)
closed_castlist_tag = re.compile(r"</castlist\W", re.I)
page_tag = re.compile(r"<pb\W", re.I)
n_attribute = re.compile(r'n="([^"]*)', re.I)
line_group_tag = re.compile(r"<lg\W", re.I)
closed_line_group = re.compile(r"</lg\W", re.I)
line_tag = re.compile(r"<l\W", re.I)
ab_tag = re.compile(r"<ab\W", re.I)
closed_line_tag = re.compile(r"</l\W", re.I)
closed_ab_tag = re.compile(r"</ab\W", re.I)
sentence_tag = re.compile(r"<s\W", re.I)
closed_sentence_tag = re.compile(r"</s\W", re.I)
front_tag = re.compile(r"<front\W", re.I)
closed_front_tag = re.compile(r"</front\W", re.I)
attrib_matcher = re.compile(r"""(\S+)="?((?:.(?!"?\s+(?:\S+)=|[>"]))+.)"?""", re.I)
tag_matcher = re.compile(r"<(\/?\w+)[^>]*>?", re.I)
head_self_close_tag = re.compile(r"<head\/>", re.I)
closed_div_tag = re.compile(r"<\/div", re.I)
head_tag = re.compile(r"<head", re.I)
closed_head_tag = re.compile(r"<\/head>", re.I)
apost_ent = re.compile(r"\&apos;", re.I)
macr_ent = re.compile(r"\&([A-Za-z])macr;", re.I)
inverted_ent = re.compile(r"\&inverted([a-zA-Z0-9]);", re.I)
supp_ent = re.compile(r"&supp([a-z0-9]);", re.I)
ligatures_ent = re.compile(r"\&([A-Za-z][A-Za-z])lig;", re.I)
type_attrib = re.compile(r'type="([^"]*)"', re.I)
hyper_div_tag = re.compile(r"<hyperdiv\W", re.I)
div_num_tag = re.compile(r"<div(.)", re.I)
char_ents = re.compile(r"\&[a-zA-Z0-9\#][a-zA-Z0-9]*;", re.I)
newline_shortener = re.compile(r"\n\n*")
check_if_char_word = re.compile(r"\w", re.I | re.U)
cap_char_or_num = re.compile(r"[A-Z0-9]")  # Capitals
ending_punctuation = re.compile(r"[%s]$" % string.punctuation.replace(")", "").replace("]", ""))
add_tag = re.compile(r"<add\W", re.I)
seg_attrib = re.compile(r"<seg \w+=", re.I)
abbrev_expand = re.compile(r'(<abbr .*expan=")([^"]*)("[^>]*>)([^>]*)(</abbr>)', re.I | re.M)
semi_colon_strip = re.compile(r"\A;?(\w+);?\Z")
h_tag = re.compile(r"<h(\d)>", re.I)

## Build a list of control characters to remove
## http://stackoverflow.com/questions/92438/stripping-non-printable-characters-from-a-string-in-python/93029#93029
tab_newline = re.compile(r"[\n|\t]")
control_chars = "".join(
    [i for i in [chr(x) for x in list(range(0, 32)) + list(range(127, 160))] if not tab_newline.search(i)]
)
control_char_re = re.compile(r"[%s]" % re.escape(control_chars))

# Entities regexes
entity_regex = [
    re.compile(r"(\&space;)", re.I),
    re.compile(r"(\&mdash;)", re.I),
    re.compile(r"(\&nbsp;)", re.I),
    re.compile(r"(\&para;)", re.I),
    re.compile(r"(\&sect;)", re.I),
    re.compile(r"(\&ast;)", re.I),
    re.compile(r"(\&commat;)", re.I),
    re.compile(r"(\&ldquo;)", re.I),
    re.compile(r"(\&laquo;)", re.I),
    re.compile(r"(\&rdquo;)", re.I),
    re.compile(r"(\&raquo;)", re.I),
    re.compile(r"(\&lsquo;)", re.I),
    re.compile(r"(\&rsquo;)", re.I),
    re.compile(r"(\&quot;)", re.I),
    re.compile(r"(\&sup[0-9]*;)", re.I),
    re.compile(r"(\&mdash;)", re.I),
    re.compile(r"(\&amp;)", re.I),
    re.compile(r"(\&deg;)", re.I),
    re.compile(r"(\&ndash;)", re.I),
    re.compile(r"(\&copy;)", re.I),
    re.compile(r"(\&gt;)", re.I),
    re.compile(r"(\&lt;)", re.I),
    re.compile(r"(\&frac[0-9]*;)", re.I),
    re.compile(r"(\&pound;)", re.I),
    re.compile(r"(\&colon;)", re.I),
    re.compile(r"(\&hyphen;)", re.I),
    re.compile(r"(\&dash;)", re.I),
    re.compile(r"(\&excl;)", re.I),
    re.compile(r"(\&dagger;)", re.I),
    re.compile(r"(\&ddagger;)", re.I),
    re.compile(r"(\&times;)", re.I),
    re.compile(r"(\&blank;)", re.I),
    re.compile(r"(\&dollar;)", re.I),
    re.compile(r"(\&cent;)", re.I),
    re.compile(r"(\&verbar;)", re.I),
    re.compile(r"(\&quest;)", re.I),
    re.compile(r"(\&hellip;)", re.I),
    re.compile(r"(\&percnt;)", re.I),
    re.compile(r"(\&middot;)", re.I),
    re.compile(r"(\&plusmn;)", re.I),
    re.compile(r"(\&sqrt;)", re.I),
    re.compile(r"(\&sol;)", re.I),
    re.compile(r"(\&sdash;)", re.I),
    re.compile(r"(\&equals;)", re.I),
    re.compile(r"(\&ornament;)", re.I),
    re.compile(r"(\&rule;)", re.I),
    re.compile(r"(\&prime;)", re.I),
    re.compile(r"(\&rsqb;)", re.I),
    re.compile(r"(\&lsqb;)", re.I),
    re.compile(r"(\&punc;)", re.I),
    re.compile(r"(\&cross;)", re.I),
    re.compile(r"(\&diamond;)", re.I),
    re.compile(r"(\&lpunctel;)", re.I),
    re.compile(r"(\&lsemicol;)", re.I),
    re.compile(r"(\&plus;)", re.I),
    re.compile(r"(\&minus;)", re.I),
    re.compile(r"(\&ounce;)", re.I),
    re.compile(r"(\&rindx;)", re.I),
    re.compile(r"(\&lindx;)", re.I),
    re.compile(r"(\&leaf;)", re.I),
    re.compile(r"(\&radic;)", re.I),
    re.compile(r"(\&dram;)", re.I),
    re.compile(r"(\&sun;)", re.I),
]

LINE_SPLITTER = re.compile(r"([^\n]+)")


class DocumentContent:
    """Content of document: a generator functionning like a list"""

    def __init__(self, content):
        self.lines = LINE_SPLITTER.finditer(content)
        self.read_ahead = deque()
        self.read_ahead_count = 0
        self.line_count = 0

    def __iter__(self):
        return self

    def __next__(self):
        self.line_count += 1
        if self.read_ahead_count != 0:
            self.read_ahead_count -= 1
            line = self.read_ahead.popleft()
            return line
        try:
            line = next(self.lines)
            return line.groups()[0]
        except StopIteration:
            raise StopIteration

    def __getitem__(self, item):
        self.read_ahead_count += 1
        line = next(self.lines).groups()[0]
        self.read_ahead.append(line)
        return line


class XMLParser:
    """Parses clean or dirty XML.
    This is a port of the PhiloLogic3 parser originally written by Mark Olsen in Perl.
    """

    def __init__(
        self,
        output,
        docid,
        filesize,
        words_to_index=None,
        known_metadata={},
        tag_to_obj_map=DEFAULT_TAG_TO_OBJ_MAP,
        metadata_to_parse=DEFAULT_METADATA_TO_PARSE,
        file_type="xml",
        **parse_options,
    ):
        """Initialize class"""
        self.types = ["doc", "div1", "div2", "div3", "para", "sent", "word"]
        self.parallel_type = "page"
        self.output = output
        self.docid = docid
        self.tag_to_obj_map = tag_to_obj_map
        self.metadata_to_parse = {}
        for obj in metadata_to_parse:
            self.metadata_to_parse[obj] = set(metadata_to_parse[obj])

        # Initialize an OHCOVector Stack. operations on this stack produce all parser output.
        self.v = CompoundStack(
            self.types,
            self.parallel_type,
            docid=docid,
            out=output,
            ref="ref",
            line="line",
            graphic="graphic",
            punctuation="punct",
        )

        self.filesize = filesize
        self.known_metadata = known_metadata

        if words_to_index:
            self.words_to_index = words_to_index
            self.defined_words_to_index = True
        else:
            self.defined_words_to_index = False

        if "file_type" in parse_options:
            self.file_type = parse_options["file_type"]
        else:
            self.file_type = "xml"

        # List of global variables used for the tag handler
        if "token_regex" in parse_options:
            self.token_regex = re.compile(r"(%s)" % parse_options["token_regex"], re.I)
        else:
            self.token_regex = re.compile(r"(%s)" % TOKEN_REGEX, re.I)

        if "sentence_breakers" in parse_options:
            self.sentence_breakers = parse_options["sentence_breakers"]
        else:
            self.sentence_breakers = []

        if "punctuation" in parse_options:
            self.punct_regex = re.compile(fr"""{parse_options["punctuation"]}""")
        else:
            self.punct_regex = re.compile(fr"{PUNCTUATION}")

        if "suppress_tags" in parse_options:
            self.suppress_tags = set([i for i in parse_options["suppress_tags"] if i])
        else:
            self.suppress_tags = []
        self.in_suppressed_tag = False
        self.current_suppressed_tag = ""

        if "break_apost" in parse_options:
            self.break_apost = parse_options["break_apost"]
        else:
            self.break_apost = True

        if "chars_not_to_index" in parse_options:
            self.chars_not_to_index = re.compile(r"%s" % parse_options["chars_not_to_index"], re.I)
        else:
            self.chars_not_to_index = re.compile(r"%s" % CHARS_NOT_TO_INDEX, re.I)

        if "break_sent_in_line_group" in parse_options:
            self.break_sent_in_line_group = parse_options["break_sent_in_line_group"]
        else:
            self.break_sent_in_line_group = False

        if "tag_exceptions" in parse_options:
            tag_exceptions = parse_options["tag_exceptions"]
        else:
            tag_exceptions = TAG_EXCEPTIONS

        tag_exceptions = "|".join(tag_exceptions)
        try:
            compiled_tag = re.compile(
                rf'({parse_options["token_regex"]})({tag_exceptions})({parse_options["token_regex"]})({tag_exceptions})({parse_options["token_regex"]})?',
                re.I | re.M,
            )
        except:
            compiled_tag = re.compile(
                rf"({TOKEN_REGEX})({tag_exceptions})({TOKEN_REGEX})({tag_exceptions})({TOKEN_REGEX})?", re.I | re.M
            )
        self.tag_exceptions = compiled_tag

        if "join_hyphen_in_words" in parse_options:
            self.join_hyphen_in_words = parse_options["join_hyphen_in_words"]
        else:
            self.join_hyphen_in_words = True

        if "unicode_word_breakers" in parse_options:
            unicode_word_breakers = parse_options["unicode_word_breakers"]
        else:
            unicode_word_breakers = UNICODE_WORD_BREAKERS
        self.unicode_word_breakers = []
        for char in unicode_word_breakers:
            compiled_char = re.compile(rb"(%s)" % char, re.I)
            self.unicode_word_breakers.append(compiled_char)

        if "abbrev_expand" in parse_options:
            self.abbrev_expand = parse_options["abbrev_expand"]
        else:
            self.abbrev_expand = True

        if "long_word_limit" in parse_options:
            self.long_word_limit = parse_options["long_word_limit"]
        else:
            self.long_word_limit = 200

        if "flatten_ligatures" in parse_options:
            self.flatten_ligatures = parse_options["flatten_ligatures"]
        else:
            self.flatten_ligatures = True

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
        self.current_div_id = ""
        self.current_div_level = 0
        self.in_seg = False

    def parse(self, text_input):
        """Top level function for reading a file and printing out the output."""
        self.input = text_input
        self.content = text_input.read()
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
        for k, v in self.known_metadata.items():
            self.v["doc"][k] = v

        # Split content into a list on newlines.
        self.content = self.content.split("\n")
        # self.content = DocumentContent(self.content)

        self.bytes_read_in = 0
        self.line_count = 0
        for line in self.content:
            # Let's start indexing words and objects at either the <text
            # of the <docbody tag.  We can add more.
            if self.in_the_text is False:
                if text_tag.search(line) or doc_body_tag.search(line) or body_tag.search(line):
                    self.in_the_text = True
                elif self.file_type == "html" and closed_head_tag.search(line):
                    self.in_the_text = True

            self.line_count += 1

            if line.startswith("<"):
                self.bytes_read_in += len(line.encode("utf8"))
                # TODO : implement DUMPXPATHS?
                if self.in_the_text:
                    self.tag_handler(line)
            else:
                self.word_handler(line)
                self.bytes_read_in += len(line.encode("utf8"))

        # if we have an open page, make sure we close it so it is properly stored
        if self.open_page:
            self.v.pull("page", self.bytes_read_in)
            self.open_page = False
        if self.open_div1 is True:
            self.close_div1(self.bytes_read_in)
        self.v["doc"].attrib["philo_doc_id"] = str(self.v["doc"].id[0])
        self.v.pull("doc", self.filesize)

    def cleanup_content(self):
        """Run various clean-ups before parsing."""
        # Replace carriage returns with spaces since they can give us all kinds of difficulties.
        self.content = self.content.replace("\r", " ")

        # Join hyphens
        if self.join_hyphen_in_words:
            self.content = join_hyphen_with_lb.sub(lambda match: "_" * len(match.group(1)), self.content)
            self.content = join_hyphen.sub(lambda match: "_" * len(match.group(1)), self.content)

        # Replace newlines with spaces.  Remember that we have seen lots of
        # tags with newlines, which can make a mess of things.
        self.content = self.content.replace("\n", " ")

        # Abbreviation expander
        if self.abbrev_expand:
            self.content = abbrev_expand.sub("\1\4\3\2\5", self.content)

        # An experimental inword tag spanner. For selected tags between letters, this replaces the tag with "_"
        # (in order to keep the byte count).  This is to allow indexing of words broken by tags.
        def replace_tag(m):
            if m[-1] is not None:
                return f"""{m[0]}{m[2]}{m[4]}{"_" * len(m[1])}{"_" * len(m[3])}"""
            else:
                return f"""{m[0]}{m[2]}{"_" * (len(m[1])+len(m[3]))}"""

        self.content = self.tag_exceptions.sub(lambda match: replace_tag(match.groups()), self.content)

        # Add newlines to the beginning and end of all tags
        self.content = self.content.replace("<", "\n<").replace(">", ">\n")

    def tag_handler(self, tag):
        """Tag handler for parser."""
        start_byte = self.bytes_read_in - len(tag.encode("utf8"))
        try:
            tag_name = tag_matcher.findall(tag)[0]
        except IndexError:
            tag_name = "unparsable_tag"
        if tag_name.replace("/", "") == self.current_suppressed_tag and tag.startswith("</"):
            self.in_suppressed_tag = False
            self.current_suppressed_tag = ""
        elif tag_name in self.suppress_tags:
            self.in_suppressed_tag = True
            self.current_suppressed_tag = tag_name
        else:
            if not tag_name.startswith("/"):
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
                if self.in_a_note:
                    do_this_para = False
                if self.no_deeper_objects:
                    do_this_para = False
                if do_this_para:
                    if self.open_para:  # account for unclosed paragraph tags
                        para_end_byte = self.bytes_read_in - len(tag.encode("utf8"))
                        self.close_para(para_end_byte)
                    self.v.push("para", tag_name, start_byte)
                    self.get_object_attributes(tag, tag_name, "para")
                    self.open_para = True

            # Notes: treat as para objects and set flag to not set paras in notes.
            elif note_tag.search(tag):
                if self.open_para:  # account for unclosed paragraph tags
                    para_end_byte = self.bytes_read_in - len(tag.encode("utf8"))
                    self.close_para(para_end_byte)
                self.open_para = True
                self.v.push("para", tag_name, start_byte)
                self.get_object_attributes(tag, tag_name, "para")
                self.in_a_note = True

            # Epigraph: treat as paragraph objects
            elif epigraph_tag.search(tag):
                if self.open_para:  # account for unclosed paragraph tags
                    para_end_byte = self.bytes_read_in - len(tag.encode("utf8"))
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
                    para_end_byte = self.bytes_read_in - len(tag.encode("utf8"))
                    self.close_para(para_end_byte)
                self.open_para = True
                self.v.push("para", tag_name, start_byte)
                self.get_object_attributes(tag, tag_name, "para")

            # SPEECH BREAKS: treat them as para objects
            elif speaker_tag.search(tag):
                if self.open_para:  # account for unclosed paragraph tags
                    para_end_byte = self.bytes_read_in - len(tag.encode("utf8"))
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
                    para_end_byte = self.bytes_read_in - len(tag.encode("utf8"))
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
                    para_end_byte = self.bytes_read_in - len(tag.encode("utf8"))
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
                    para_end_byte = self.bytes_read_in - len(tag.encode("utf8"))
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
                    para_end_byte = self.bytes_read_in - len(tag.encode("utf8"))
                    self.close_para(para_end_byte)
                self.open_para = True
                self.v.push("para", tag_name, start_byte)
                self.get_object_attributes(tag, tag_name, "para")
            elif closed_stage_tag.search(tag) and not self.no_deeper_objects:
                self.close_para(self.bytes_read_in)
                self.open_para = False

            # CAST LIST: treat them as para objects
            elif castlist_tag.search(tag):
                if self.open_para:  # account for unclosed paragraph tags
                    para_end_byte = self.bytes_read_in - len(tag.encode("utf8"))
                    self.close_para(para_end_byte)
                self.open_para = True
                self.v.push("para", tag_name, start_byte)
                self.get_object_attributes(tag, tag_name, "para")

            # Handle <add> tags as a para.
            elif add_tag.search(tag):
                if self.open_para:  # account for unclosed paragraph tags
                    para_end_byte = self.bytes_read_in - len(tag.encode("utf8"))
                    self.close_para(para_end_byte)
                self.open_para = True
                self.v.push("para", tag_name, start_byte)
                self.get_object_attributes(tag, tag_name, "para")
                self.no_deeper_objects = True
            elif tag == "</add>":
                self.close_para(self.bytes_read_in)
                self.no_deeper_objects = False

            # PAGE BREAKS: this updates the currentpagetag or sets it to "na" if not found.
            elif page_tag.search(tag):
                if self.open_page:
                    page_end_tag = self.bytes_read_in - len(tag.encode("utf8"))
                    self.v.pull("page", page_end_tag)
                    self.open_page = False
                self.v.push("page", tag_name, start_byte)
                self.get_object_attributes(tag, tag_name, "page")
                try:
                    n = self.v["page"]["n"]
                    n = n.replace(" ", "_").replace("-", "_").lower()
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
                    para_end_byte = self.bytes_read_in - len(tag.encode("utf8"))
                    self.close_para(para_end_byte)
                self.open_para = True
                self.v.push("para", tag_name, start_byte)
                self.get_object_attributes(tag, tag_name, "para")
            elif closed_line_group.search(tag):
                self.in_line_group = False
                self.close_para(self.bytes_read_in)

            # END LINE TAG: use this to break "sentences" if self.in_line_group.  This is
            # if to set searching in line groups to lines rather than sentences.
            elif line_tag.search(tag):
                if self.in_line_group and self.break_sent_in_line_group:
                    self.v.push("sent", tag_name, start_byte)
                    self.v.pull("sent", self.bytes_read_in)
                # Create line parallel object
                self.v.push("line", tag_name, start_byte)
                self.get_object_attributes(tag, tag_name, "line")
                self.v["line"].attrib["doc_id"] = self.docid
            elif closed_line_tag.search(tag):
                if self.in_line_group and self.break_sent_in_line_group:
                    self.v.pull("sent", self.bytes_read_in)
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
                self.current_div_id = self.v["div1"].id
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
                self.current_div_id = self.v["div1"].id
                self.v["div1"].attrib["philo_div1_id"] = " ".join(str(i) for i in self.v["div1"].id[:2])
                self.context_div_level = 1
                self.open_div1 = True
                div_head = self.get_div_head(tag)
                if "[NA]" in div_head or "[na]" in div_head:
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
                self.current_div_id = self.v["div1"].id
                self.v["div1"]["head"] = "[HyperDiv]"

            # h1, h2, h3 tags should be considered markers for divs in HTML files
            # what follows the h tags are the content for that div, so we use implied close
            if self.file_type == "html" and h_tag.search(tag):
                self.context_div_level = int(h_tag.search(tag).groups()[0])
                if self.context_div_level > 3:
                    self.content_div_level = 3
                if self.context_div_level == 1:
                    if self.open_div1:
                        self.close_div1(start_byte)
                    self.open_div1 = True
                elif self.context_div_level == 2:
                    if self.open_div2:
                        self.close_div2(start_byte)
                    self.open_div2 = True
                elif self.context_div_level == 3:
                    if self.open_div3:
                        self.close_div3(start_byte)
                    self.open_div3 = True
                current_div = "div%d" % self.context_div_level
                self.v.push(current_div, tag_name, start_byte)
                look_ahead = self.line_count
                read_more = True
                div_head = ""
                while read_more:
                    try:
                        next_line = self.content[look_ahead]
                    except IndexError:
                        break
                    if re.search(r"</h1|h2|h3>", next_line, re.I):
                        break
                    div_head += next_line
                    look_ahead += 1
                div_head = self.clear_char_ents(div_head)
                div_head = self.latin1_ents_to_utf8(div_head)
                div_head = self.convert_other_ents(div_head)
                div_head = re.sub(r"\n?<[^>]*>\n?", "", div_head)
                div_head = div_head.replace("_", "")
                div_head = div_head.replace("\t", "")
                div_head = " ".join(div_head.split())  # remove double or more spaces
                div_head = div_head.replace("[", "").replace("]", "")
                div_head = div_head.replace('"', "")
                div_head = div_head.strip()
                div_head = self.remove_control_chars(div_head)
                div_head = convert_entities(div_head)
                div_head = div_head.replace('"', "")
                self.v[current_div]["head"] = div_head

            # DIV TAGS: set division levels and print out div info. A couple of assumptions:
            # - I assume divs are numbered 1,2,3.
            # - I output <head> info where I find it.  This could also be modified to output
            #   a structured table record with div type, and other attributes, along with
            #   the Philoid and head for searching under document levels.
            elif closed_div_tag.search(tag):
                if "div1" in tag_name:
                    if self.in_front_matter:
                        self.close_div2(self.bytes_read_in)
                    else:
                        self.close_div1(self.bytes_read_in)
                elif "div2" in tag_name:
                    if self.in_front_matter:
                        self.close_div3(self.bytes_read_in)
                    else:
                        self.close_div2(self.bytes_read_in)
                elif "div3" in tag_name:
                    self.close_div3(self.bytes_read_in)
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

                # TODO: ignore divs inside of internal text tags.  Setable
                # from configuration.  But we will bump the para and sent args
                div_type = "div%d" % div_level
                if div_type == "div1":
                    if self.open_div1:
                        self.close_div1(start_byte)
                    self.open_div1 = True
                    self.v.push("div1", tag_name, start_byte)
                    self.current_div_id = self.v["div1"].id
                    self.v["div1"]["head"] = self.get_div_head(tag)
                    self.get_object_attributes(tag, tag_name, object_type="div1")
                elif div_type == "div2":
                    if self.open_div2:
                        self.close_div2(start_byte)
                    self.open_div2 = True
                    self.v.push("div2", tag_name, start_byte)
                    self.current_div_id = self.v["div2"].id
                    self.v["div2"]["head"] = self.get_div_head(tag)
                    self.get_object_attributes(tag, tag_name, object_type="div2")
                else:
                    if self.open_div3:
                        self.close_div3(start_byte)
                    self.open_div3 = True
                    self.v.push("div3", tag_name, start_byte)
                    self.current_div_id = self.v["div3"].id
                    self.v["div3"]["head"] = self.get_div_head(tag)
                    self.get_object_attributes(tag, tag_name, object_type="div3")

                if "type" in self.v[div_type]:
                    if self.v[div_type]["type"] == "notes":
                        self.no_deeper_objects = True

                # We are handling the case of index tags containing attributes which describe the parent div
                # the type attrib has its value in the value attrib
            elif tag_name == "index" and self.context_div_level != 0:
                attrib = dict(self.get_attributes(tag))
                div = "div%d" % self.context_div_level
                if "type" in attrib:
                    if attrib["type"] in self.metadata_to_parse["div"]:
                        try:
                            self.v[div].attrib[attrib["type"]] = attrib["value"]
                        except KeyError:
                            pass
                else:
                    for metadata_name, metadata_value in attrib.items():
                        self.v[div].attrib[metadata_name] = metadata_value

            elif tag_name == "date":
                div = "div%d" % self.context_div_level
                for attrib_name, attrib_value in self.get_attributes(tag):
                    if attrib_name == "value" or attrib_name == "when":
                        if "div_date" not in self.v[div].attrib:
                            self.v[div].attrib["div_date"] = attrib_value
                    else:
                        attrib_name = f"div_{attrib_name}"
                        if attrib_name not in self.v[div].attrib:
                            self.v[div].attrib[attrib_name] = attrib_value

            elif tag_name == "ref":
                self.v.push("ref", tag_name, start_byte)
                self.get_object_attributes(tag, tag_name, "ref")
                self.v["ref"].attrib["parent"] = " ".join([str(i) for i in self.current_div_id])
                self.v.pull("ref", self.bytes_read_in)

            elif tag_name == "graphic":
                self.v.push("graphic", tag_name, start_byte)
                self.get_object_attributes(tag, tag_name, "graphic")
                self.v["graphic"].attrib["parent"] = " ".join([str(i) for i in self.current_div_id])
                self.v.pull("graphic", self.bytes_read_in)

    def word_handler(self, words):
        """
        Word handler. It takes an artbitrary string or words between two tags and
        splits them into words. It also identifies sentence breaks.  I am not checking for existing sentence
        tags, but could and conditionalize it. Also note that it does not check for
        sentences inside of linegroups ... which are typically broken on lines.
        I am not currently handling ";" at the end of words because of confusion with
        character ents. Easily fixed.
        """

        if self.in_suppressed_tag is False:
            # We don't like many character entities, so let's change them
            # into spaces to get a clean break.
            if char_ents.search(words):
                words = self.clear_char_ents(words)

            if self.unicode_word_breakers:
                for word_breaker in self.unicode_word_breakers:
                    words = word_breaker.sub(lambda match: b" " * len(match.group(1)), words.encode("utf8")).decode(
                        "utf8"
                    )

            # we're splitting the line of words into distinct words
            # separated by "\n"
            words = self.token_regex.sub(r"\n\1\n", words)

            if self.break_apost:
                words = words.replace("'", "\n'\n")

            words = newline_shortener.sub(r"\n", words)

            current_pos = self.bytes_read_in
            count = 0
            word_list = words.split("\n")
            last_word = ""
            next_word = ""
            if self.in_the_text:
                for word in word_list:
                    word_in_utf8 = word.encode("utf8")
                    word_length = len(word_in_utf8)
                    try:
                        next_word = word_list[count + 1]
                    except IndexError:
                        pass
                    count += 1

                    # Keep track of your bytes since this is where you are getting
                    # the byte offsets for words.
                    current_pos += word_length

                    # Do we have a word? At least one of these characters.
                    if check_if_char_word.search(word.replace("_", "")):
                        last_word = word
                        word_pos = current_pos - len(word_in_utf8)
                        if "&" in word:
                            # Convert ents to utf-8
                            word = self.latin1_ents_to_utf8(word)
                            # Convert other ents to things....
                            word = self.convert_other_ents(word)

                        # You may have some semi-colons...
                        if ";" in word:
                            if "&" in word:
                                pass  # TODO
                            else:
                                word = semi_colon_strip.sub(r"\1", word)  # strip on both ends

                        # Get rid of certain characters that don't break words, but don't index.
                        # These are defined in a compiled regex below: chars_not_to_index
                        word = self.chars_not_to_index.sub("", word)

                        # TODO: Call a function to distinguish between words beginning with an
                        # upper case and lower case character.  This USED to be a proper
                        # name split in ARTFL, but we don't see many databases with proper
                        # names tagged.

                        # Switch everything to lower case
                        word = word.lower()

                        # Check to see if the word is longer than we want.  More than 235
                        # characters appear to cause problems in the indexer.
                        if len(word) > self.long_word_limit:
                            print("Long word in {}: {}".format(self.input.name, word), file=sys.stderr)
                            print("Truncating to %d characters for index..." % self.long_word_limit, file=sys.stderr)
                            word = word[: self.long_word_limit]

                        word = self.remove_control_chars(word)
                        word = word.replace("_", "").strip()
                        word = word.replace(" ", "")
                        if word:
                            if self.defined_words_to_index:
                                if word not in self.words_to_index:
                                    continue
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
                        elif "." in word:
                            is_sent = True
                            if len(last_word) < 3:
                                if cap_char_or_num.search(last_word):
                                    is_sent = False

                            # Periods in numbers don't break sentences.
                            if next_word.islower() or next_word.isdigit():
                                is_sent = False

                        elif word in self.sentence_breakers:
                            is_sent = True

                        if is_sent:
                            # a little hack--we don't know the punctuation mark that will end a sentence
                            # until we encounter it--so instead, we let the push on "word" create a
                            # implicit philo_virtual sentence, then change its name once we actually encounter
                            # the punctuation token.
                            if "sent" not in self.v:
                                self.v.push("sent", word.replace("\t", " ").strip(), current_pos)
                            self.v["sent"].name = word.replace("\t", " ").strip()
                            self.v.pull("sent", current_pos + len(word.encode("utf8")))
                        elif self.punct_regex.search(word):
                            punc_pos = current_pos - len(word.encode("utf8"))
                            punct = word.strip()
                            punct = punct.replace("\t", " ")
                            punct = self.remove_control_chars(punct)
                            for single_punct in punct:
                                end_pos = len(single_punct.encode("utf8"))
                                if single_punct != " ":
                                    self.v.push("punct", single_punct, punc_pos)
                                    self.v.pull("punct", punc_pos + len(single_punct.encode("utf8")))
                                punc_pos = end_pos

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
        if self.open_div3 is True:
            self.v["div3"].attrib["philo_div3_id"] = " ".join(str(i) for i in self.v["div3"].id[:4])
            self.v.pull("div3", end_byte)
            self.open_div3 = False

    def close_div2(self, end_byte):
        """Close div2 objects."""
        if self.open_div3:
            self.close_div3(end_byte)
        if self.open_div2 is True:
            self.v["div2"].attrib["philo_div2_id"] = " ".join(str(i) for i in self.v["div2"].id[:3])
            self.v.pull("div2", end_byte)
            self.open_div2 = False

    def close_div1(self, end_byte):
        """Close div1 objects."""
        if self.open_div2:
            self.close_div2(end_byte)
        if self.open_div1 is True:
            self.v["div1"].attrib["philo_div1_id"] = " ".join(str(i) for i in self.v["div1"].id[:2])
            self.v.pull("div1", end_byte)
            self.open_div1 = False

    def camel_case_to_snake_case(self, word):
        word = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", word)
        word = re.sub("([a-z0-9])([A-Z])", r"\1_\2", word).lower()
        return word

    def get_attributes(self, tag):
        """Find all attributes for any given tag."""
        attribs = []
        for attrib, value in attrib_matcher.findall(tag):
            # Replace ":" with "_" for attribute names since they are illegal in SQLite
            attrib = attrib.replace(":", "_")
            value = self.remove_control_chars(value)
            value = ending_punctuation.sub("", value.strip())
            value = convert_entities(value)
            value = value.replace('"', "")
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
                    try:
                        next_line = self.content[look_ahead]
                    except IndexError:
                        break
                    if closed_head_tag.search(next_line):
                        read_more = False
                    elif overflow_trap > 50:  # Overflow trap in case you miss </head
                        read_more = False
                    else:
                        div_head += next_line
        if div_head:
            div_head = self.clear_char_ents(div_head)
            div_head = self.latin1_ents_to_utf8(div_head)
            div_head = self.convert_other_ents(div_head)
            div_head = re.sub(r"\n?<[^>]*>\n?", "", div_head)
            div_head = div_head.replace("_", "")
            div_head = div_head.replace("\t", "")
            div_head = " ".join(div_head.split())  # remove double or more spaces
            div_head = div_head.replace("[", "").replace("]", "")
            div_head = div_head.replace('"', "")
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
            div_head = "[NA]"

        div_head = self.remove_control_chars(div_head)
        div_head = convert_entities(div_head)
        div_head = div_head.replace('"', "")
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
        text_in_bytes = text.encode("utf8")
        if self.flatten_ligatures:
            text_in_bytes = text_in_bytes.replace(b"&AElig;", b"\xc3\x86")
            text_in_bytes = text_in_bytes.replace(b"&szlig;", b"\xc3\x9F")
            text_in_bytes = text_in_bytes.replace(b"&aelig;", b"\xc3\xA6")
        text_in_bytes = text_in_bytes.replace(b"&Agrave;", b"\xc3\x80")
        text_in_bytes = text_in_bytes.replace(b"&Aacute;", b"\xc3\x81")
        text_in_bytes = text_in_bytes.replace(b"&Acirc;", b"\xc3\x82")
        text_in_bytes = text_in_bytes.replace(b"&Atilde;", b"\xc3\x83")
        text_in_bytes = text_in_bytes.replace(b"&Auml;", b"\xc3\x84")
        text_in_bytes = text_in_bytes.replace(b"&Aring;", b"\xc3\x85")
        text_in_bytes = text_in_bytes.replace(b"&Ccedil;", b"\xc3\x87")
        text_in_bytes = text_in_bytes.replace(b"&Egrave;", b"\xc3\x88")
        text_in_bytes = text_in_bytes.replace(b"&Eacute;", b"\xc3\x89")
        text_in_bytes = text_in_bytes.replace(b"&Ecirc;", b"\xc3\x8A")
        text_in_bytes = text_in_bytes.replace(b"&Euml;", b"\xc3\x8B")
        text_in_bytes = text_in_bytes.replace(b"&Igrave;", b"\xc3\x8C")
        text_in_bytes = text_in_bytes.replace(b"&Iacute;", b"\xc3\x8D")
        text_in_bytes = text_in_bytes.replace(b"&Icirc;", b"\xc3\x8E")
        text_in_bytes = text_in_bytes.replace(b"&Iuml;", b"\xc3\x8F")
        text_in_bytes = text_in_bytes.replace(b"&ETH;", b"\xc3\x90")
        text_in_bytes = text_in_bytes.replace(b"&Ntilde;", b"\xc3\x91")
        text_in_bytes = text_in_bytes.replace(b"&Ograve;", b"\xc3\x92")
        text_in_bytes = text_in_bytes.replace(b"&Oacute;", b"\xc3\x93")
        text_in_bytes = text_in_bytes.replace(b"&Ocirc;", b"\xc3\x94")
        text_in_bytes = text_in_bytes.replace(b"&Otilde;", b"\xc3\x95")
        text_in_bytes = text_in_bytes.replace(b"&Ouml;", b"\xc3\x96")
        text_in_bytes = text_in_bytes.replace(b"&#215;", b"\xc3\x97")  # MULTIPLICATION SIGN
        text_in_bytes = text_in_bytes.replace(b"&Oslash;", b"\xc3\x98")
        text_in_bytes = text_in_bytes.replace(b"&Ugrave;", b"\xc3\x99")
        text_in_bytes = text_in_bytes.replace(b"&Uacute;", b"\xc3\x9A")
        text_in_bytes = text_in_bytes.replace(b"&Ucirc;", b"\xc3\x9B")
        text_in_bytes = text_in_bytes.replace(b"&Uuml;", b"\xc3\x9C")
        text_in_bytes = text_in_bytes.replace(b"&Yacute;", b"\xc3\x9D")
        text_in_bytes = text_in_bytes.replace(b"&THORN;", b"\xc3\x9E")
        text_in_bytes = text_in_bytes.replace(b"&agrave;", b"\xc3\xA0")
        text_in_bytes = text_in_bytes.replace(b"&aacute;", b"\xc3\xA1")
        text_in_bytes = text_in_bytes.replace(b"&acirc;", b"\xc3\xA2")
        text_in_bytes = text_in_bytes.replace(b"&atilde;", b"\xc3\xA3")
        text_in_bytes = text_in_bytes.replace(b"&auml;", b"\xc3\xA4")
        text_in_bytes = text_in_bytes.replace(b"&aring;", b"\xc3\xA5")
        text_in_bytes = text_in_bytes.replace(b"&ccedil;", b"\xc3\xA7")
        text_in_bytes = text_in_bytes.replace(b"&egrave;", b"\xc3\xA8")
        text_in_bytes = text_in_bytes.replace(b"&eacute;", b"\xc3\xA9")
        text_in_bytes = text_in_bytes.replace(b"&ecirc;", b"\xc3\xAA")
        text_in_bytes = text_in_bytes.replace(b"&euml;", b"\xc3\xAB")
        text_in_bytes = text_in_bytes.replace(b"&igrave;", b"\xc3\xAC")
        text_in_bytes = text_in_bytes.replace(b"&iacute;", b"\xc3\xAD")
        text_in_bytes = text_in_bytes.replace(b"&icirc;", b"\xc3\xAE")
        text_in_bytes = text_in_bytes.replace(b"&iuml;", b"\xc3\xAF")
        text_in_bytes = text_in_bytes.replace(b"&eth;", b"\xc3\xB0")
        text_in_bytes = text_in_bytes.replace(b"&ntilde;", b"\xc3\xB1")
        text_in_bytes = text_in_bytes.replace(b"&ograve;", b"\xc3\xB2")
        text_in_bytes = text_in_bytes.replace(b"&oacute;", b"\xc3\xB3")
        text_in_bytes = text_in_bytes.replace(b"&ocirc;", b"\xc3\xB4")
        text_in_bytes = text_in_bytes.replace(b"&otilde;", b"\xc3\xB5")
        text_in_bytes = text_in_bytes.replace(b"&ouml;", b"\xc3\xB6")
        text_in_bytes = text_in_bytes.replace(b"&#247;", b"\xc3\xB7")  # DIVISION SIGN
        text_in_bytes = text_in_bytes.replace(b"&oslash;", b"\xc3\xB8")
        text_in_bytes = text_in_bytes.replace(b"&ugrave;", b"\xc3\xB9")
        text_in_bytes = text_in_bytes.replace(b"&uacute;", b"\xc3\xBA")
        text_in_bytes = text_in_bytes.replace(b"&ucirc;", b"\xc3\xBB")
        text_in_bytes = text_in_bytes.replace(b"&uuml;", b"\xc3\xBC")
        text_in_bytes = text_in_bytes.replace(b"&yacute;", b"\xc3\xBD")
        text_in_bytes = text_in_bytes.replace(b"&thorn;", b"\xc3\xBE")
        text_in_bytes = text_in_bytes.replace(b"&yuml;", b"\xc3\xBF")

        # Greek Entities for HTML4 and Chadwock Healey -- Charles Cooney
        text_in_bytes = text_in_bytes.replace(b"&agr;", b"\xce\xb1")
        text_in_bytes = text_in_bytes.replace(b"&alpha;", b"\xce\xb1")
        text_in_bytes = text_in_bytes.replace(b"&bgr;", b"\xce\xb2")
        text_in_bytes = text_in_bytes.replace(b"&beta;", b"\xce\xb2")
        text_in_bytes = text_in_bytes.replace(b"&ggr;", b"\xce\xb3")
        text_in_bytes = text_in_bytes.replace(b"&gamma;", b"\xce\xb3")
        text_in_bytes = text_in_bytes.replace(b"&dgr;", b"\xce\xb4")
        text_in_bytes = text_in_bytes.replace(b"&delta;", b"\xce\xb4")
        text_in_bytes = text_in_bytes.replace(b"&egr;", b"\xce\xb5")
        text_in_bytes = text_in_bytes.replace(b"&epsilon;", b"\xce\xb5")
        text_in_bytes = text_in_bytes.replace(b"&zgr;", b"\xce\xb6")
        text_in_bytes = text_in_bytes.replace(b"&zeta;", b"\xce\xb6")
        text_in_bytes = text_in_bytes.replace(b"&eegr;", b"\xce\xb7")
        text_in_bytes = text_in_bytes.replace(b"&eta;", b"\xce\xb7")
        text_in_bytes = text_in_bytes.replace(b"&thgr;", b"\xce\xb8")
        text_in_bytes = text_in_bytes.replace(b"&theta;", b"\xce\xb8")
        text_in_bytes = text_in_bytes.replace(b"&igr;", b"\xce\xb9")
        text_in_bytes = text_in_bytes.replace(b"&iota;", b"\xce\xb9")
        text_in_bytes = text_in_bytes.replace(b"&kgr;", b"\xce\xba")
        text_in_bytes = text_in_bytes.replace(b"&kappa;", b"\xce\xba")
        text_in_bytes = text_in_bytes.replace(b"&lgr;", b"\xce\xbb")
        text_in_bytes = text_in_bytes.replace(b"&lambda;", b"\xce\xbb")
        text_in_bytes = text_in_bytes.replace(b"&mgr;", b"\xce\xbc")
        text_in_bytes = text_in_bytes.replace(b"&mu;", b"\xce\xbc")
        text_in_bytes = text_in_bytes.replace(b"&ngr;", b"\xce\xbd")
        text_in_bytes = text_in_bytes.replace(b"&nu;", b"\xce\xbd")
        text_in_bytes = text_in_bytes.replace(b"&xgr;", b"\xce\xbe")
        text_in_bytes = text_in_bytes.replace(b"&xi;", b"\xce\xbe")
        text_in_bytes = text_in_bytes.replace(b"&ogr;", b"\xce\xbf")
        text_in_bytes = text_in_bytes.replace(b"&omicron;", b"\xce\xbf")
        text_in_bytes = text_in_bytes.replace(b"&pgr;", b"\xcf\x80")
        text_in_bytes = text_in_bytes.replace(b"&pi;", b"\xcf\x80")
        text_in_bytes = text_in_bytes.replace(b"&rgr;", b"\xcf\x81")
        text_in_bytes = text_in_bytes.replace(b"&rho;", b"\xcf\x81")
        text_in_bytes = text_in_bytes.replace(b"&sfgr;", b"\xcf\x82")
        text_in_bytes = text_in_bytes.replace(b"&sigmaf;", b"\xcf\x82")
        text_in_bytes = text_in_bytes.replace(b"&sgr;", b"\xcf\x83")
        text_in_bytes = text_in_bytes.replace(b"&sigma;", b"\xcf\x83")
        text_in_bytes = text_in_bytes.replace(b"&tgr;", b"\xcf\x84")
        text_in_bytes = text_in_bytes.replace(b"&tau;", b"\xcf\x84")
        text_in_bytes = text_in_bytes.replace(b"&ugr;", b"\xcf\x85")
        text_in_bytes = text_in_bytes.replace(b"&upsilon;", b"\xcf\x85")
        text_in_bytes = text_in_bytes.replace(b"&phgr;", b"\xcf\x86")
        text_in_bytes = text_in_bytes.replace(b"&phi;", b"\xcf\x86")
        text_in_bytes = text_in_bytes.replace(b"&khgr;", b"\xcf\x87")
        text_in_bytes = text_in_bytes.replace(b"&chi;", b"\xcf\x87")
        text_in_bytes = text_in_bytes.replace(b"&psgr;", b"\xcf\x88")
        text_in_bytes = text_in_bytes.replace(b"&psi;", b"\xcf\x88")
        text_in_bytes = text_in_bytes.replace(b"&ohgr;", b"\xcf\x89")
        text_in_bytes = text_in_bytes.replace(b"&omega;", b"\xcf\x89")
        text_in_bytes = text_in_bytes.replace(b"&Agr;", b"\xce\x91")
        text_in_bytes = text_in_bytes.replace(b"&Alpha;", b"\xce\x91")
        text_in_bytes = text_in_bytes.replace(b"&Bgr;", b"\xce\x92")
        text_in_bytes = text_in_bytes.replace(b"&Beta;", b"\xce\x92")
        text_in_bytes = text_in_bytes.replace(b"&Ggr;", b"\xce\x93")
        text_in_bytes = text_in_bytes.replace(b"&Gamma;", b"\xce\x93")
        text_in_bytes = text_in_bytes.replace(b"&Dgr;", b"\xce\x94")
        text_in_bytes = text_in_bytes.replace(b"&Delta;", b"\xce\x94")
        text_in_bytes = text_in_bytes.replace(b"&Egr;", b"\xce\x95")
        text_in_bytes = text_in_bytes.replace(b"&Epsilon;", b"\xce\x95")
        text_in_bytes = text_in_bytes.replace(b"&Zgr;", b"\xce\x96")
        text_in_bytes = text_in_bytes.replace(b"&Zeta;", b"\xce\x96")
        text_in_bytes = text_in_bytes.replace(b"&EEgr;", b"\xce\x97")
        text_in_bytes = text_in_bytes.replace(b"&Eta;", b"\xce\x97")
        text_in_bytes = text_in_bytes.replace(b"&THgr;", b"\xce\x98")
        text_in_bytes = text_in_bytes.replace(b"&Theta;", b"\xce\x98")
        text_in_bytes = text_in_bytes.replace(b"&Igr;", b"\xce\x99")
        text_in_bytes = text_in_bytes.replace(b"&Iota;", b"\xce\x99")
        text_in_bytes = text_in_bytes.replace(b"&Kgr;", b"\xce\x9a")
        text_in_bytes = text_in_bytes.replace(b"&Kappa;", b"\xce\x9a")
        text_in_bytes = text_in_bytes.replace(b"&Lgr;", b"\xce\x9b")
        text_in_bytes = text_in_bytes.replace(b"&Lambda;", b"\xce\x9b")
        text_in_bytes = text_in_bytes.replace(b"&Mgr;", b"\xce\x9c")
        text_in_bytes = text_in_bytes.replace(b"&Mu;", b"\xce\x9c")
        text_in_bytes = text_in_bytes.replace(b"&Ngr;", b"\xce\x9d")
        text_in_bytes = text_in_bytes.replace(b"&Nu;", b"\xce\x9d")
        text_in_bytes = text_in_bytes.replace(b"&Xgr;", b"\xce\x9e")
        text_in_bytes = text_in_bytes.replace(b"&Xi;", b"\xce\x9e")
        text_in_bytes = text_in_bytes.replace(b"&Ogr;", b"\xce\x9f")
        text_in_bytes = text_in_bytes.replace(b"&Omicron;", b"\xce\x9f")
        text_in_bytes = text_in_bytes.replace(b"&Pgr;", b"\xce\xa0")
        text_in_bytes = text_in_bytes.replace(b"&Pi;", b"\xce\xa0")
        text_in_bytes = text_in_bytes.replace(b"&Rgr;", b"\xce\xa1")
        text_in_bytes = text_in_bytes.replace(b"&Rho;", b"\xce\xa1")
        text_in_bytes = text_in_bytes.replace(b"&Sgr;", b"\xce\xa3")
        text_in_bytes = text_in_bytes.replace(b"&Sigma;", b"\xce\xa3")
        text_in_bytes = text_in_bytes.replace(b"&Tgr;", b"\xce\xa4")
        text_in_bytes = text_in_bytes.replace(b"&Tau;", b"\xce\xa4")
        text_in_bytes = text_in_bytes.replace(b"&Ugr;", b"\xce\xa5")
        text_in_bytes = text_in_bytes.replace(b"&Upsilon;", b"\xce\xa5")
        text_in_bytes = text_in_bytes.replace(b"&PHgr;", b"\xce\xa6")
        text_in_bytes = text_in_bytes.replace(b"&Phi;", b"\xce\xa6")
        text_in_bytes = text_in_bytes.replace(b"&KHgr;", b"\xce\xa7")
        text_in_bytes = text_in_bytes.replace(b"&Chi;", b"\xce\xa7")
        text_in_bytes = text_in_bytes.replace(b"&PSgr;", b"\xce\xa8")
        text_in_bytes = text_in_bytes.replace(b"&Psi;", b"\xce\xa8")
        text_in_bytes = text_in_bytes.replace(b"&OHgr;", b"\xce\xa9")
        text_in_bytes = text_in_bytes.replace(b"&Omega;", b"\xce\xa9")
        return text_in_bytes.decode("utf8")

    def convert_other_ents(self, text):
        """ handles character entities in index words.
        There should not be many of these."""
        text = text.replace("&apos;", "'")
        text = text.replace("&s;", "s")
        text = macr_ent.sub(r"\1", text)
        text = inverted_ent.sub(r"\1", text)
        text = supp_ent.sub(r"\1", text)
        if self.flatten_ligatures:
            text = ligatures_ent.sub(r"\1", text)
        return text

    def remove_control_chars(self, text):
        return control_char_re.sub("", text)


if __name__ == "__main__":
    for docid, fn in enumerate(sys.argv[1:], 1):
        print(docid, fn, file=sys.stderr)
        size = os.path.getsize(fn)
        fh = open(fn)
        parser = XMLParser(
            sys.stdout,
            docid,
            size,
            known_metadata={"filename": fn},
            tag_to_obj_map=DEFAULT_TAG_TO_OBJ_MAP,
            metadata_to_parse=DEFAULT_METADATA_TO_PARSE,
        )
        parser.parse(fh)
