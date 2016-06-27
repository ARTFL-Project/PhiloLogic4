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
navigable_objects = ('doc', 'div1', 'div2', 'div3')

# Define filters as a list of functions to call, either those in Loader or outside
filters = LoadFilters.DefaultLoadFilters
post_filters = PostFilters.DefaultPostFilters

## Define text objects to generate plain text files for various machine learning tasks
## For instance, this could be ['doc', 'div1']
plain_text_obj = []
if plain_text_obj:
    filters.extend([store_in_plain_text(*plain_text_obj)])
</code></pre>

For now, it's just important to know what options can be specified in the load script:

`default_object_level` defines the type of object returned for the purpose of most navigation reports--for most database, this will be "doc", but you might want to use "div1" for dictionary or encyclopedia databases.

`navigable_objects` is a list of the object types stored in the database and available for searching, reporting, and navigation--("doc","div1","div2","div3") is the default, but you might want to append "para" if you are parsing interesting metadata on paragraphs, like in drama.  Pages are handled separately, and don't need to be included here.

`filters` and `post_filters` are lists of loader functions--their behavior and design will be documented separately, but they are basically lists of modular loader functions to be executed in order, and so shouldn't be modified carelessly.

`plain_text_obj` is a very useful option that generates a flat text file representations of all objects of a given type, like "doc" or "div1", usually for data mining with Mallet or some other tool.

#### Configuring the XML Parser ####
The next section of the load script is setup for the XML Parser:

<pre><code>
## Set-up database load ###
###########################

doc_xpaths =  NewParser.DefaultDocXPaths

metadata_fields = NewParser.DefaultMetadataToParse

pseudo_empty_tags = []

## A list of tags to ignore
suppress_tags = []

token_regex = NewParser.TokenRegex

# Define a file (with full path) containing words to filter out. Must be one word per line.
# Useful for dirty OCR.
filtered_words_list = ""

## Define the order in which files are sorted
## This will affect the order in which results are displayed
## Supply a list of metadata strings, e.g.:
## ["date", "author", "title"]
sort_order = ["year", "author", "title", "filename"]
</code></pre>

The basic layout is this:

`doc_xpaths` is a dictionary that maps philologic document-level object contained in the TEI header to absolute XPaths--that is, XPaths evaluated where `.` refers to the TEI document root element.  You can define multiple XPaths for the same type of object, but you will get much better and more consistent results if you do not.

`metadata_fields` is a dictionary that maps one or more non-document-level object types to a list of metadata (usually attributes) to retrieve. . e.g.:
<pre><code>
DefaultMetadataToParse = {
    "div": ["head", "type", "n", "id"],
    "para": ["who"],
    "page": ["n", "id", "fac"],
    "ref": ["target", "n", "type"]
}
</code></pre>
`pseudo_empty_tags` is a very obscure option for things that you want to treat as containers, even if they are encoded as self-closing tags.  

`suppress_tags` is a list of tags in which you do not want to perform tokenization at all--that is, no words in them will be searchable via full-text search.  It does not prohibit extracting metadata from the content of those tags.

`token_regex` is a regular expression used to drive our tokenizer. 

`sort_order` is a list of metadata fields which defines the order in which the parser will load and store files in the database. This affects the default order in which search results are returned.

So to use a load config file as an argument, you would run the following:

`philoload4 -l load_config.py db_name path_to_files`

And that's it!


