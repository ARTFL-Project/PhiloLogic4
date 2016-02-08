import sys
import os
import philologic
from philologic.Parser import Parser
from philologic.Loader import Loader, handle_command_line, setup_db_dir


##################################################
## Don't edit unless you know what you're doing ##
##################################################

os.environ["LC_ALL"] = "C" # Exceedingly important to get uniform sort order.
os.environ["PYTHONIOENCODING"] = "utf-8"


#############
## Globals ##
#############

LoadFilters = philologic.LoadFilters
PostFilters = philologic.PostFilters

## Parse command line
dbname, files, workers, debug = handle_command_line(sys.argv)

LOAD_OPTIONS = {}

##########################
## System Configuration ##
##########################

# Set the filesytem path to the root web directory for your PhiloLogic install.
database_root = None
# /var/www/html/philologic/ is conventional for linux,
# /Library/WebServer/Documents/philologic for Mac OS.
# Please follow the instructions in INSTALLING before use.

# Set the URL path to the same root directory for your philologic install.
url_root = None
# http://localhost/philologic/ is appropriate if you don't have a DNS hostname.

if database_root is None or url_root is None:
    print >> sys.stderr, "Please configure the loader script before use.  See INSTALLING in your PhiloLogic distribution."
    exit()

## This should be set to the location of the PhiloLogic4 directory
web_app_dir = ""
# The load process will fail if you haven't set up the template_dir at the correct location.


############################
##### Indexing Options #####
############################

## Define default object level
# default_object_level = "doc"

## Define navigable objects
# navigable_objects = ('doc', 'div1', 'div2', 'div3')

## Data tables to store.
# tables = ['toms', 'pages', 'words']

## Define filters as a list of functions to call, either those in LoadFilters or outside
# filters = [normalize_unicode_raw_words, make_word_counts, generate_words_sorted,
#            make_object_ancestors, make_sorted_toms, prev_next_obj, generate_pages,
#            make_max_id]

## Define post_filters (run after file parsing)
# post_filters = [word_frequencies, normalized_word_frequencies, metadata_frequencies, normalized_metadata_frequencies]

## Define text objects to generate plain text files for various machine learning tasks
## For instance, this could be ['doc', 'div1']
plain_text_obj = []
if plain_text_obj:
    filters.extend([store_in_plain_text(*plain_text_obj)])

extra_locals = {"db_url": url_root + dbname}
extra_locals['default_object_level'] = default_object_level

###########################
## Set-up database load ###
###########################

xpaths =  [("doc","."),("div",".//div1"),("div",".//div2"),("div",".//div3"),("para",".//sp"),("page",".//pb")]

metadata_xpaths = [ # metadata per type.  '.' is in this case the base element for the type, as specified in XPaths above.
    # MUST MUST MUST BE SPECIFIED IN OUTER TO INNER ORDER--DOC FIRST, WORD LAST
    ("doc","./teiHeader//titleStmt/title","title"),
    ("doc","./teiHeader//titleStmt/author","author"),
    ("doc", "./text/front//docDate/@value", "date"),
    ("div","./head","head"),
    ("div",".@n","n"),
    ("div",".@id","id"),
    ("para", ".@who", "who"),
    ("page",".@n","n"),
    ("page",".@fac","img")
]

pseudo_empty_tags = ["milestone"]

## A list of tags to ignore
suppress_tags = ["teiHeader",".//head"]

word_regex = r"([\w]+)"
punct_regex = r"([\.?!])"

token_regex = word_regex + "|" + punct_regex

## Saved in db.locals.py for tokenizing at runtime
extra_locals["word_regex"] = word_regex
extra_locals["punct_regex"] = punct_regex



db_destination = database_root + dbname
data_destination = db_destination + "/data"
db_url = url_root + dbname

## Store all defined options for database load
for option in Loader.VALID_OPTIONS:
    LOAD_OPTIONS[option] = locals()[option]

if __name__ == "__main__":

    setup_db_dir(db_destination, web_app_dir)


    ####################
    ## Load the files ##
    ####################

    l = Loader(**LOAD_OPTIONS)
    l.add_files(files)
    filenames = l.list_files()
    ## The following line creates a list of the files to parse and sorts the files by filename
    ## Should you need to supply a custom sort order from the command line you need to supply the files variable,
    ## defined at the top of this script, instead of filenames, like so:
    ## load_metadata = [{"filename":f} for f in files]
    load_metadata = [{"filename":f} for f in sorted(filenames)]
    l.parse_files(workers,load_metadata)
    l.merge_objects()
    l.analyze()
    l.setup_sql_load()
    l.post_processing()
    l.finish(**extra_locals)
