import sys
import os
import errno
import philologic

from philologic.LoadFilters import *
from philologic.PostFilters import *
from philologic.Parser import Parser
from philologic.Loader import Loader, handle_command_line, setup_db_dir

try:
    import artfl_xpaths
except ImportError:
    print "## Error ###\nYou need to copy the artfl_xpaths.py script from PhiloLogic4/scripts/ in the same directory as this script"
    exit()

## Flush buffer output
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

## Parse command line
dbname, files, workers, console_output, log, debug = handle_command_line(sys.argv)


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

template_dir = "~/PhiloLogic4/www/"
# The load process will fail if you haven't set up the template_dir at the correct location.

# Define default object level
default_object_level = 'doc'

# Define navigable objects
navigable_objects = ('doc', 'div1', 'div2', 'div3')

# Data tables to store.
tables = ['toms', 'pages', 'words']

# Define filters as a list of functions to call, either those in Loader or outside
filters = [normalize_unicode_raw_words,make_word_counts,generate_words_sorted,make_object_ancestors(*navigable_objects),
           make_sorted_toms(*navigable_objects),prev_next_obj(*navigable_objects),generate_pages, make_max_id]
post_filters = [word_frequencies,normalized_word_frequencies,metadata_frequencies,normalized_metadata_frequencies]

## Define text objects to generate plain text files for various machine learning tasks
## For instance, this could be ['doc', 'div1']
plain_text_obj = []
if plain_text_obj:
    filters.extend([store_in_plain_text(*plaint_text_obj)])

extra_locals = {"db_url": url_root + dbname}
extra_locals['default_object_level'] = default_object_level

###########################
## Set-up database load ###
###########################

xpaths =  artfl_xpaths.xpaths        

metadata_xpaths = artfl_xpaths.metadata_xpaths

pseudo_empty_tags = ["milestone"]

## A list of tags to ignore
suppress_tags = ["teiHeader",".//head"]

word_regex = r"([\w]+)"
punct_regex = r"([\.?!])"

token_regex = word_regex + "|" + punct_regex 

## Saved in db.locals.py for tokenizing at runtime
extra_locals["word_regex"] = word_regex
extra_locals["punct_regex"] = punct_regex

## Define the order in which files are sorted
## This will affect the order in which results are displayed
## Supply a list of metadata strings, e.g.:
## ["date", "author", "title"]
sort_order = ["date", "author", "title", "filename"]

################################
## Don't edit unless you know ##
## what you're doing          ##
################################

os.environ["LC_ALL"] = "C" # Exceedingly important to get uniform sort order.
os.environ["PYTHONIOENCODING"] = "utf-8"
    
db_destination = database_root + dbname
data_destination = db_destination + "/data"
db_url = url_root + dbname

if __name__ == "__main__":

    setup_db_dir(db_destination, template_dir, force_delete=True)


    ####################
    ## Load the files ##
    ####################

    l = Loader(data_destination,
             load_filters=filters,
             post_filters=post_filters,
             tables=tables,
             xpaths=xpaths,
             metadata_xpaths=metadata_xpaths,
             pseudo_empty_tags=pseudo_empty_tags,
             suppress_tags=suppress_tags,
             token_regex=token_regex,
             default_object_level=default_object_level,
             debug=debug)

    l.add_files(files)
    filenames = l.list_files()
    if sort_order == None:
      load_metadata = [{"filename":f} for f in sorted(filenames)]
    else:
      load_metadata = l.sort_by_metadata(*sort_order)
    l.parse_files(workers,load_metadata)
    l.merge_objects()
    l.analyze()
    l.setup_sql_load()
    l.post_processing()
    l.finish(**extra_locals)

    print >> sys.stderr, "Application viewable at", db_url