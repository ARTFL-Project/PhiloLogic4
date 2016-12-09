Database Loading
================

Loading PhiloLogic databases is very straight forward, and most of the time, you shouldn't need to specify any specialized load option. 

A few important notes:
* Before loading any databases, you should first make sure the global configuration file located in `/etc/philologic/philologic4.cfg has been edited appropriately. For more info, see [here](installation.md#global-config)
* The PhiloLogic4 Parser's behavior is configurable from an external load config file, though only to a certain extent. You can also supply a replacement Parser class if you need to.
* The loading process is designed to be short, and easy to understand and configure.

## Executing the load command ##

In order for PhiloLogic to index your files, you need to execute the `philoload4` command. The basic command is run as so:

`philoload4 [database_name] [path_to_files]``

The `philoload4` command requires the following required arguments::

1.  the name of the database to create, which will be the subdirectory
    into your web space directory, i.e. ``/var/www/html/mydatabase``,
2.  the paths to each of the files you wish to load,
    i.e. ``mycorpus/xml/*.xml``.

`philoload4` also accepts a number of optional command line arguments::

  `-h`, `--help`        show this help message and exit
  
  `-a WEB_APP_DIR`, `--app_dir=WEB_APP_DIR`     Define custom location for the web app directory
                        
  `-b BIBLIOGRAPHY`, `--bibliography=BIBLIOGRAPHY`      Defines a file containing the document-level bibliography of the texts
                        
  `-c CORES`, `--cores=CORES`       define the number of cores used for parsing
                        
  `-d`, `--debug`           add debugging at parse time
  
  `-f`, `--force_delete`    overwrite database without confirmation
  
  `-F`, `--file-list`       Defines whether the file argument is a file containing fullpaths to the files to load
                        
  `-H HEADER`, `--header=HEADER`        define header type (tei or dc) of files to parse
                        
  `-l LOAD_CONFIG`, `--load_config=LOAD_CONFIG`     load external config for specialized load
                        
  `-t FILE_TYPE`, `--file-type=FILE_TYPE`       Define file type for parsing: plain_text or xml

So our command for loading texts could be::

`philoload4 -c 8 -d my_database files/*xml`


#### Database Load Configuration ####

In the event you need to customize the behavior of the parser, you can pass the `-l` option along with a `load_config.py` file to be found in `PhiloLogic4/extras/` directory. In this file, you can configure a number of different parameters:

<pre><code>
# Define default object level
default_object_level = 'doc'

# Define navigable objects
navigable_objects = ('doc', 'div1', 'div2', 'div3', 'para')

## Define text objects to generate plain text files for various machine learning tasks
## For instance, this could be ['doc', 'div1']
plain_text_obj = []

## Define whether to store all words with their philo IDs. Useful for data-mining tasks
## where keeping the index information (and byte offset) is important.
store_words_and_ids = False
</code></pre>

`default_object_level` defines the type of object returned for the purpose of most navigation reports--for most database, this will be "doc", but you might want to use "div1" for dictionary or encyclopedia databases.

`navigable_objects` is a list of the object types stored in the database and available for searching, reporting, and navigation--("doc","div1","div2","div3") is the default, but you might want to append "para" if you are parsing interesting metadata on paragraphs, like in drama.  Pages are handled separately, and don't need to be included here.

`filters` and `post_filters` are lists of loader functions--their behavior and design will be documented separately, but they are basically lists of modular loader functions to be executed in order, and so shouldn't be modified carelessly.

`plain_text_obj` is a very useful option that generates a flat text file representations of all objects of a given type, like "doc" or "div1", usually for data mining with Mallet or some other tool.

`store_words_and_ids` defines whether you want the parser to save a representation of the text containing the individual index ID for each word in all texts indexed in the DB. This can be useful for data-mining task that need to know about word positioning such as sequence alignment.

#### Configuring the XML Parser ####
The next section of the load script is setup for the XML Parser:

<pre><code>
## Set-up database load ###
###########################

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

## A list of tags to ignore
suppress_tags = []

# This regex defines how to tokenize words and punctuation
token_regex = "([\&A-Za-z0-9\177-\377][\&A-Za-z0-9\177-\377\_\';]*)"

# Define a file (with full path) containing words to index. Must be one word per line.
# Useful for filtering out dirty OCR.
words_to_index = ""

# Define the order in which files are sorted. This will affect the order in which
# results are displayed. Supply a list of metadata strings, e.g.:
# ["date", "author", "title"]
sort_order = ["year", "author", "title", "filename"]

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
</code></pre>

The basic layout is this:

`doc_xpaths` is a dictionary that maps philologic document-level object contained in the TEI header to absolute XPaths--that is, XPaths evaluated where `.` refers to the TEI document root element.  You can define multiple XPaths for the same type of object, but you will get much better and more consistent results if you do not.

`tag_to_obj_map` is a dictionary that maps XML tags to the standard types PhiloLogic stores in its index.

`metadata_to_parse` is a dictionary that maps one or more non-document-level object types to a list of metadata (usually attributes) to retrieve.

`suppress_tags` is a list of tags in which you do not want to perform tokenization at all--that is, no words in them will be searchable via full-text search.  It does not prohibit extracting metadata from the content of those tags.

`token_regex` is a regular expression used to drive our tokenizer. 

`words_to_index` is a file containing all words that should be indexed. You'd want to define this in the event you're dealing with dirty OCR and would end up with way too many unique words, which would blow up the index, or just kill search performance. Leaving this empty means that all words will be indexed.

`sort_order` is a list of metadata fields which defines the order in which the parser will load and store files in the database. This affects the default order in which search results are returned.

The remaining options are self-explanatory given the comments...

So to use a load config file as an argument, you would run the following:

`philoload4 -l load_config.py db_name path_to_files`

And that's it!


