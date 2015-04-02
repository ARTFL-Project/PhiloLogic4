Database Loading
================

Loading PhiloLogic databases requires two separate steps:
* [Configuring the loading script](#sysconfig)
* [Executing the loading script with command-line arguments](#loading)

## <a name="sysconfig">Configuring the loading script ##

A few important notes:
* The load script is not installed system-wide--you generally want to keep it near your data, with any other scripts. 
* The load script has no global configuration file--all configuration is kept separate in each copy of the script that you create.
* The PhiloLogic4 Parser class is fully configurable from the load script--you can change any Xpaths you want, or even supply a replacement Parser class if you need to.
* The load script is designed to be short, and easy to understand and modify.

The most important pieces of information in any load script are the system setup variables at the top of the file.  These will give immediate errors if they aren't set up right. 

You can find the load script in extras/load_script.py. 

#### System Configuration ####

<pre><code>
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

template_dir = database_root + "_system_dir/_install_dir/"
# The load process will fail if you haven't set up the template_dir at the correct location.

# Define default object level
default_object_level = 'doc'
</code></pre>

`database_root` is the filesystem path to the web-accessible directory where your PhiloLogic4 database will live, like /var/www/philologic/--so your webserver process will need read access to it, and you will need write access to create the database--and don't forget to keep the slash at the end of the directory, or you'll get errors.  

`url_root` is the HTTP URL that the database_root directory is accessible at: http://your.server.com/philologic/could be a reasonable mapping of the example above, but it will depend on your DNS setup, server configuration, and other hosting issues outside the scope of this document.

`template_dir`, which defaults to database_root + "/_system_dir/_install_dir/", is the directory containing all the scripts, reports, templates, and stylesheets that make up a PhiloLogic4 database application.  If you have customized behaviors or designs that you want reflected in all of the databases you build, you can keep those templates in a directory on their own where they won't get overwritten.  

At the moment, you can't "clone" the templates from an existing database, because they actual database content can be very large, but we'd very much like to implement that feature in the future to allow for easy reloads.

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

## <a name="loading">Running the load script ##

Once all files are in place and ``load_script.py`` script is customized, it's time
for PhiloLogic to actually index your text files, by running the script
on TEI-XML files::

    python ~/mycorpus/load_script.py [database name] [path to TEI-XML files]

This script takes the following required arguments:

1.  the name of the database to create, which will be the subdirectory
    into ``/var/www/html`` directory, i.e. ``mydatabase``,
2.  the paths to each of `TEI-XML` files from which fulfill database content,
    i.e. ``~/mycorpus/xml/*.xml``.

The full list of arguments ``load_script.py`` accepts will be displayed  when running ``loader.py`` without
a database name::

    python ~/mycorpus/load_script.py

The script also accepts optional arguments, among others most common are::
``--workers`` and ``--debug``:

``-w WORKERS`` / ``--workers=WORKERS``:
    This option set the number of workers the ``loader.py`` will use.
    It is mostly usefull for multi-cores hardware.

``-d`` / ``--debug``
    Set both ``load_script.py`` and web application in debug mode.

So our command line for loading would be::

    cd /var/www/html
    python ~/mycorpus/load_script.py mydatabase ~/mycorpus/xml/*.xml

The above command should have populated the ``/var/www/html/mydatabase``
directory with both web application and data files.
