Database Loading
================

Loading PhiloLogic databases is very straight forward, and most of the time, you shouldn't need to specify any specialized load option. 

A few important notes:
* Before loading any databases, you should first make sure the global configuration file located in `/etc/philologic/philologic4.cfg has been edited appropriately. For more info, see [here](../installation.md)
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

So our command line for loading could be::

`philoload4 -c 8 -d my_database files/*xml`


#### Database Configuration ####

Most of the rest of the file is configuration for the Loader class, which does all of the real work, but the config is kept here, in the script, so you don't have to maintain custom classes for every database. 

<pre><code>
# Define default object level
default_object_level = 'doc'

# Define navigable objects
navigable_objects = ('doc', 'div1', 'div2', 'div3')

# Data tables to store.
tables = ['toms', 'pages']

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
</code></pre>

For now, it's just important to know what options can be specified in the load script:

`default_object_level` defines the type of object returned for the purpose of most navigation reports--for most database, this will be "doc", but you might want to use "div1" for dictionary or encyclopedia databases.

`navigable_objects` is a list of the object types stored in the database and available for searching, reporting, and navigation--("doc","div1","div2","div3") is the default, but you might want to append "para" if you are parsing interesting metadata on paragraphs, like in drama.  Pages are handled separately, and don't need to be included here.

`filters` and `post_filters` are lists of loader functions--their behavior and design will be documented separately, but they are basically lists of modular loader functions to be executed in order, and so shouldn't be modified carelessly.

`plain_text_obj` is a very useful option that generates a flat text file representations of all objects of a given type, like "doc" or "div1", usually for data mining with Mallet or some other tool.

`extra_locals` is a catch_all list of extra parameters to pass on to your database later, if you need to--think of it as a "swiss army knife" for passing data from the loader to the database at run-time.

#### Configuring the XML Parser ####
The next section of the load script is setup for the XML Parser:

<pre><code>
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
</code></pre>

The basic layout is this:

`xpaths` is a list of 2-tuples that maps philologic object types to absolute XPaths--that is, XPaths evaluated where `.` refers to the TEI document root element.  You can define multiple XPaths for the same type of object, but you will get much better and more consistent results if you do not.

`metadata_xpaths` is a list of 3-tuples that map one or more XPaths to each metadata field defined on each object type.  These are evaluated relative to whatever XML element matched the XPath for the object type in question--so `.` here refers to a `doc`, `div1`, or paragraph-level object somewhere in the xml.

`pseudo_empty_tags` is a very obscure option for things that you want to treat as containers, even if they are encoded as self-closing tags.  

`suppress_tags` is a list of tags in which you do not want to perform tokenization at all--that is, no words in them will be searchable via full-text search.  It does not prohibit extracting metadata from the content of those tags.

`word_regex` and `punct_regex` are regular expression fragments that drive our tokenizer.  Each needs to consist of exactly one capturing subgroup so that our tokenizer can use them correctly. They are both fully unicode-aware--usually, the default `\w` class is fine for words, but in some cases you may need to add apostrophes and such to the word pattern.  
Likewise, the punctuation regex pattern fully supports multi-byte utf-8 punctuation.  In both cases you should enter characters as unicode code points, not utf-8 byte strings.

#### Construct the Loader object ####

The following 2 sections are where all the work gets done, and an important place to perform modifications.   First, we construct the Loader object, passing it all the configuration variables we have constructed so far:

<pre><code>
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
</code></pre>

Then we operate the Loader object step-by-step:

<pre><code>
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
</code></pre>

And that's it!  

Usually, these load functions should all be executed in the same order, but it is worth paying special attention to the `load_metadata variable` that is constructed right before `l.parse_files` is called.  This variable controls the entire parsing process, and is incredibly powerful.  Not only does it let you define any order in which to load your files, but you can also supply any document-level metadata you wish, and change the xpaths, load_filters, or parser class used per file, which can be very useful on complex or heterogeneous data sets.  However, this often requires either some source of stand-off metadata or pre-processing/parsing stage.  

For this purpose, we've added a powerful new Loader function called `sort_by_metadata` which integrates the functions of a PhiloLogic3 style metadata guesser and sorter, while still being modular enough to replaced entirely when necessary.


