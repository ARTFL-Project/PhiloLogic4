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

## Define whether to store all words with their philo IDs. Useful for data-mining tasks
## where keeping the index information (and byte offset) is important.
store_words_and_ids = False

#####################
## Parsing Options ##
#####################

# These are doc level XPATHS used to parse a standard TEI header.
# These XPATHS need to be inside a <teiHeader> and strictly apply to the entire document..
# Only useful if you parse a TEI header.
doc_xpaths = {
    "author": [
        ".//sourceDesc/bibl/author[@type='marc100']", ".//sourceDesc/bibl/author[@type='artfl']",
        ".//sourceDesc/bibl/author", ".//titleStmt/author", ".//sourceDesc/biblStruct/monogr/author/name",
        ".//sourceDesc/biblFull/titleStmt/author", ".//sourceDesc/biblFull/titleStmt/respStmt/name",
        ".//sourceDesc/biblFull/titleStmt/author", ".//sourceDesc/bibl/titleStmt/author"
    ],
    "title": [
        ".//sourceDesc/bibl/title[@type='marc245']", ".//sourceDesc/bibl/title[@type='artfl']",
        ".//sourceDesc/bibl/title", ".//titleStmt/title", ".//sourceDesc/bibl/titleStmt/title",
        ".//sourceDesc/biblStruct/monogr/title", ".//sourceDesc/biblFull/titleStmt/title"
    ],
    "author_dates": [
        ".//sourceDesc/bibl/author/date", ".//titlestmt/author/date"
    ],
    "create_date": [
        ".//profileDesc/creation/date", ".//fileDesc/sourceDesc/bibl/imprint/date",
        ".//sourceDesc/biblFull/publicationStmt/date", ".//profileDesc/dummy/creation/date",
        ".//fileDesc/sourceDesc/bibl/creation/date"
    ],
    "publisher": [
        ".//sourceDesc/bibl/imprint[@type='artfl']", ".//sourceDesc/bibl/imprint[@type='marc534']",
        ".//sourceDesc/bibl/imprint/publisher", ".//sourceDesc/biblStruct/monogr/imprint/publisher/name",
        ".//sourceDesc/biblFull/publicationStmt/publisher", ".//sourceDesc/bibl/publicationStmt/publisher",
        ".//sourceDesc/bibl/publisher", ".//publicationStmt/publisher", ".//publicationStmp"
    ],
    "pub_place": [
        ".//sourceDesc/bibl/imprint/pubPlace", ".//sourceDesc/biblFull/publicationStmt/pubPlace",
        ".//sourceDesc/biblStruct/monog/imprint/pubPlace", ".//sourceDesc/bibl/pubPlace",
        ".//sourceDesc/bibl/publicationStmt/pubPlace"
    ],
    "pub_date": [
        ".//sourceDesc/bibl/imprint/date", ".//sourceDesc/biblStruct/monog/imprint/date",
        ".//sourceDesc/biblFull/publicationStmt/date", ".//sourceDesc/bibFull/imprint/date", ".//sourceDesc/bibl/date",
        ".//text/front/docImprint/acheveImprime"
    ],
    "extent": [
        ".//sourceDesc/bibl/extent", ".//sourceDesc/biblStruct/monog//extent", ".//sourceDesc/biblFull/extent"
    ],
    "editor": [
        ".//sourceDesc/bibl/editor", ".//sourceDesc/biblFull/titleStmt/editor", ".//sourceDesc/bibl/title/Stmt/editor"
    ],
    "identifiers": [
        ".//publicationStmt/idno"
    ],
    "text_genre": [
        ".//profileDesc/textClass/keywords[@scheme='genre']/term", ".//SourceDesc/genre"
    ],
    "keywords": [
        ".//profileDesc/textClass/keywords/list/item"
    ],
    "language": [
        ".//profileDesc/language/language"
    ],
    "notes": [
        ".//fileDesc/notesStmt/note", ".//publicationStmt/notesStmt/note"
    ],
    "auth_gender": [
        ".//publicationStmt/notesStmt/note"
    ],
    "collection": [
        ".//seriesStmt/title"
    ],
    "period": [
        ".//profileDesc/textClass/keywords[@scheme='period']/list/item", ".//SourceDesc/period", ".//sourceDesc/period"
    ],
    "text_form": [
        ".//profileDesc/textClass/keywords[@scheme='form']/term"
    ],
    "structure": [
        ".//SourceDesc/structure", ".//sourceDesc/structure"
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
    "graphic": "graphic"
}

# Defines which metadata to parse out for each object. All metadata defined here are attributes of a tag,
# with the exception of head which is its own tag. Below are defaults.
metadata_to_parse = {
    "div": ["head", "type", "n", "id", "vol"],
    "para": ["who", "resp", "id"],
    "page": ["n", "id", "fac"],
    "ref": ["target", "n", "type"],
    "graphic": ["url"]
}

# This regex defines how to tokenize words and punctuation
token_regex = "[\&A-Za-z0-9\177-\377][\&A-Za-z0-9\177-\377\_\';]*"

# Define a file (with full path) containing words to index. Must be one word per line.
# Useful for filtering out dirty OCR.
words_to_index = ""

# Define the order in which files are sorted. This will affect the order in which
# results are displayed. Supply a list of metadata strings, e.g.:
# ["date", "author", "title"]
sort_order = ["year", "author", "title", "filename"]

## A list of tags to ignore: contents will not be indexed
suppress_tags = []

# --------------------- Set Apostrophe Break ------------------------
# Set to True to break words on apostrophe.  Probably False for
# English, True for French.  Your milage may vary.
break_apost = True

# ------------- Define Characters to Exclude from Index words -------
# Leading to a second list, characters which can be in words
# but you don't want to index.
chars_not_to_index = "\[\{\]\}"

# ---------------------- Treat Lines as Sentences --------------------
# In linegroups, break sentence objects on </l> and turns off
# automatic sentence recognition.  Normally off.
break_sent_in_line_group = False

# ------------------ Skip in word tags -------------------------------
# Tags normally break words.  There may be exceptions.  To run the
# exception, turn on the exception and list them as patterns.
# Tags will not be indexed and will not break words. An empty list turns of the feature
tag_exceptions = ['<hi[^>]*>', '<emph[^>]*>', '<\/hi>', '<\/emph>', '<orig[^>]*>', '<\/orig>', '<sic[^>]*>', '<\/sic>',
                  '<abbr[^>]*>', '<\/abbr>', '<i>', '</i>', '<sup>', '</sup>']

# ------------- UTF8 Strings to consider as word breakers -----------
# In SGML, these are ents.  But in Unicode, these are characters
# like any others.  Consult the table at:
# www.utf8-chartable.de/unicode-utf8-table.pl?start=8016&utf8=dec&htmlent=1
# to see about others. An empty list disables the feature.
unicode_word_breakers = ['\xe2\x80\x93',  # U+2013 &ndash; EN DASH
                         '\xe2\x80\x94',  # U+2014 &mdash; EM DASH
                         '\xc2\xab',  # &laquo;
                         '\xc2\xbb',  # &raquo;
                         '\xef\xbc\x89',  # fullwidth right parenthesis
                         '\xef\xbc\x88',  # fullwidth left parenthesis
                         '\xe2\x80\x90',  # U+2010 hyphen for greek stuff
                         '\xce\x87',  # U+00B7 ano teleia
                         '\xe2\x80\xa0',  # U+2020 dagger
                         '\xe2\x80\x98',  # U+2018 &lsquo; LEFT SINGLE QUOTATION
                         '\xe2\x80\x99',  # U+2019 &rsquo; RIGHT SINGLE QUOTATION
                         '\xe2\x80\x9c',  # U+201C &ldquo; LEFT DOUBLE QUOTATION
                         '\xe2\x80\x9d',  # U+201D &rdquo; RIGHT DOUBLE QUOTATION
                         '\xe2\x80\xb9',  # U+2039 &lsaquo; SINGLE LEFT-POINTING ANGLE QUOTATION
                         '\xe2\x80\xba',  # U+203A &rsaquo; SINGLE RIGHT-POINTING ANGLE QUOTATION
                         '\xe2\x80\xa6'  # U+2026 &hellip; HORIZONTAL ELLIPSIS
                        ]

#  ----------------- Set Long Word Limit  -------------------
#  Words greater than 235 characters (bytes) cause an indexing
#  error.  This sets a limit.  Words are then truncated to fit.
long_word_limit = 200

# ------------------ Hyphenated Word Joiner ----------------------------
# Softhypen word joiner.  At this time, I'm trying to join
# words broken by &shy;\n and possibly some additional
# selected tags.  Could be extended.
join_hyphen_in_words = True

# ------------------ Abbreviation Expander for Indexing. ---------------
# This is to handle abbreviation tags.  I have seen two types:
#       <abbr expan="en">&emacr;</abbr>
#       <abbr expan="Valerius Maximus">Val. Max.</abbr>
# For now, lets's try the first.
abbrev_expand = True

# ---------------------- Flatten Ligatures for Indexing --------------
# Convert SGML ligatures to base characters for indexing.
# &oelig; = oe.  Leave this on.  At one point we should think
# Unicode, but who knows if this is important.
flatten_ligatures = True

# Define a list of strings which mark the end of a sentence.
# Note that this list will be added to the current one which is [".", "?", "!"]
sentence_breakers = []
