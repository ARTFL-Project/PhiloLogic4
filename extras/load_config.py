from philologic import Loader, LoadFilters, Parser, NewParser, PlainTextParser, PostFilters


###############################
## General Loading Variables ##
###############################

# Define default object level
default_object_level = Loader.DEFAULT_OBJECT_LEVEL

# Define navigable objects: doc, div1, div2, div3, para.
# The default is ["doc", "div1", "div2", "div3"]
navigable_objects = Loader.NAVIGABLE_OBJECTS

# Define filters as a list of functions to call, either those in Loader or outside
filters = LoadFilters.DefaultLoadFilters
post_filters = PostFilters.DefaultPostFilters

## Define text objects to generate plain text files for various machine learning tasks
## For instance, this could be ['doc', 'div1']
plain_text_obj = []
if plain_text_obj:
    filters.extend([store_in_plain_text(*plaint_text_obj)])

#####################
## Parsing Options ##
#####################

xpaths =  Parser.DefaultXPaths

metadata_xpaths = NewParser.DefaultMetadataXPaths

pseudo_empty_tags = []

## A list of tags to ignore
suppress_tags = []

word_regex = Parser.DefaultWordRegex
punct_regex = Parser.DafaultPunctRegex

token_regex = word_regex + "|" + punct_regex

# Define a file (with full path) containing words to filter out. Must be one word per line.
# Useful for dirty OCR.
filtered_words_list = ""

## Define the order in which files are sorted
## This will affect the order in which results are displayed
## Supply a list of metadata strings, e.g.:
## ["date", "author", "title"]
sort_order = ["date", "author", "title", "filename"]
