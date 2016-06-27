from philologic import Loader, LoadFilters, Parser, NewParser, PlainTextParser, PostFilters


###############################
## General Loading Variables ##
###############################

# Define default object level
default_object_level = "doc"

# Define navigable objects: doc, div1, div2, div3, para.
navigable_objects = ('doc', 'div1', 'div2', 'div3', 'para')

## Define text objects to generate plain text files for various machine learning tasks
## For instance, this could be ['doc', 'div1']
plain_text_obj = []

#####################
## Parsing Options ##
#####################

# These are doc level XPATHS used to parse a standard TEI header.
# These XPATHS need to be inside a <teiHeader> and strictly apply to an entire document..
# Only useful if you parse a TEI header.
doc_xpaths =  {
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
    ],
    "idno": [
        ".//fileDesc/publicationStmt/idno/"
    ]
}

# Maps any given tag to one of PhiloLogic's types. Available types are div, para, page, and ref.
# Below is the default mapping.
tag_to_obj_map = {
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
    "pb": "page",
    "ref": "ref"
}

# Defines which metadata to parse out for each object. All metadata defined here are attributes of a tag,
# with the exception of head which is its own tag. Below are defaults.
metadata_to_parse = {
    "div": ["head", "type", "n", "id", "vol"],
    "para": ["who"],
    "page": ["n", "id", "fac"],
    "ref": ["target", "n", "type"]
}

## A list of tags to ignore
suppress_tags = []

# This regex defines how to tokenize words and punctuation
token_regex = "([\&A-Za-z0-9\177-\377][\&A-Za-z0-9\177-\377\_\';]*)"

# Define a file (with full path) containing words to filter out. Must be one word per line.
# Useful for dirty OCR.
filtered_words_list = ""

# Define the order in which files are sorted. This will affect the order in which
# results are displayed. Supply a list of metadata strings, e.g.:
# ["date", "author", "title"]
sort_order = ["year", "author", "title", "filename"]
