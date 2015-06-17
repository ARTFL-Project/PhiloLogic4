#!/usr/bin/env python
import re
import os
import time
import sys
import codecs
import math
import cPickle
import subprocess
import sqlite3
from ast import literal_eval as eval
from optparse import OptionParser
from glob import glob

import philologic.Parser as Parser
import philologic.LoadFilters as LoadFilters
import philologic.PostFilters as PostFilters
from philologic.PostFilters import make_sql_table
from philologic.DB import DB
from lxml import etree
from philologic.Config import MakeWebConfig, MakeDBConfig


sort_by_word = "-k 2,2"
sort_by_id = "-k 3,3n -k 4,4n -k 5,5n -k 6,6n -k 7,7n -k 8,8n -k 9,9n"
object_types = ['doc', 'div1', 'div2', 'div3', 'para', 'sent', 'word']

blocksize = 2048 # index block size.  Don't alter.
index_cutoff = 10 # index frequency cutoff.  Don't. alter.


## While these tables are loaded by default, you can override that default, although be aware
## that you will only have reduced functionality if you do. It is strongly recommended that you
## at least keep the 'toms' table from toms.db.

default_tables = ['toms', 'pages', 'words']



class Loader(object):

    def __init__(self,destination,tables = default_tables,default_object_level='doc',
                 post_filters = None, debug=False, **parser_defaults):
        self.omax = [1,1,1,1,1,1,1,1,1]
        self.debug = debug
        self.parse_pool = None
        self.types = object_types
        self.tables = tables
        self.default_object_level = default_object_level

        self.parser_defaults = {}

        if "parser_factory" not in parser_defaults:
            parser_defaults["parser_factory"] = Parser.Parser
        if "token_regex" not in parser_defaults:
            parser_defaults["token_regex"] = Parser.DefaultTokenRegex
        if "xpaths" not in parser_defaults:
            parser_defaults["xpaths"] = Parser.DefaultXPaths
        if "metadata_xpaths" not in parser_defaults:
            parser_defaults["metadata_xpaths"] = Parser.DefaultMetadataXPaths
        if "pseudo_empty_tags" not in parser_defaults:
            parser_defaults["pseudo_empty_tags"] = []
        if "suppress_tags" not in parser_defaults:
            parser_defaults["suppress_tags"] = []
        if "load_filters" not in parser_defaults:
            parser_defaults["load_filters"] = LoadFilters.DefaultLoadFilters

        for option in ["parser_factory","token_regex","xpaths","metadata_xpaths","pseudo_empty_tags","suppress_tags","load_filters"]:
            self.parser_defaults[option] = parser_defaults[option]

        if not post_filters:
            post_filters = PostFilters.DefaultPostFilters
        self.post_filters = post_filters

        self.debug = debug

        self.sort_by_word = sort_by_word
        self.sort_by_id = sort_by_id

        try:
            os.stat(destination + "/WORK/")
            self.destination = destination
            self.is_new = False
        except OSError:
            self.setup_dir(destination)
            self.is_new = True

        self.metadata_fields = []
        self.metadata_hierarchy = []
        self.metadata_types = {}
        self.normalized_fields = []


    def setup_dir(self,path):
        os.system("mkdir -p %s" % path)
        self.workdir = path + "/WORK/"
        self.textdir = path + "/TEXT/"
        os.mkdir(self.workdir)
        os.mkdir(self.textdir)
        self.destination = path

    def add_files(self,files):
        for f in files:
            command = "cp %s %s/%s" % (shellquote(f),self.textdir, os.path.basename(f).replace(" ","_").replace("'","_")) 
            os.system(command)
        os.system("chmod 775 %s*" % self.textdir)

    def status(self):
        pass

    def list_files(self):
        return os.listdir(self.textdir)

    def pre_parse_header(self, fn):
        fh = open(fn)
        header = ""
        while True:
            line = fh.readline()
            scan = re.search("<teiheader>|<temphead>",line,re.IGNORECASE)
            if scan:
                header = line[scan.start():]
                break
        while True:
            line = fh.readline()
            scan = re.search("</teiheader>|<\/?temphead>", line, re.IGNORECASE)
            if scan:
                header = header + line[:scan.end()]
                break
            else:
                header = header + line
        tree = etree.fromstring(header)
        return tree

    def pre_parse_whole_file(self, fn):
        fh = open(fn)
        tree = etree.fromstring(fh.read())
        return tree

    def sort_by_metadata(self, *fields, **options):
        load_metadata = []
        if "reverse" in options:
            reverse = options["reverse"]
        else: reverse = False
        if "whole_file" in options:
            whole_file = options["whole_file"]
        else: whole_file = False

        for f in self.list_files():
            data = {"filename":f}
            fn = self.textdir + f
            if whole_file == True:
                tree = self.pre_parse_whole_file(fn)
            else:
                tree = self.pre_parse_header(fn)

            trimmed_metadata_xpaths = []
            for type, xpath, field in self.parser_defaults["metadata_xpaths"]:
                if type == "doc":
                    if field not in data:
                        attr_pattern_match = re.search(r"@([^\/\[\]]+)$",xpath)
                        if attr_pattern_match:
                            xp_prefix = xpath[:attr_pattern_match.start(0)]
                            attr_name = attr_pattern_match.group(1)
                            elements = tree.findall(xp_prefix)
                            for el in elements:
                                if el is not None and el.get(attr_name,""):
                                    data[field] = el.get(attr_name,"").encode("utf-8")
                                    break
                        else:
                            el = tree.find(xpath)
                            if el is not None and el.text is not None:
                                data[field] = el.text.encode("utf-8")
                else:
                    trimmed_metadata_xpaths.append( (type,xpath,field) )
            data["options"] = {"metadata_xpaths":trimmed_metadata_xpaths}
            load_metadata.append(data)

        def make_sort_key(d):
            key = [d.get(f,"") for f in fields]
            return key
        print "Load files ordered by %s" % ', '.join(fields)
        load_metadata.sort(key=make_sort_key, reverse=reverse)
        return load_metadata

    def parse_files(self,max_workers,data_dicts = None):
        print "\n### Parsing files ###"
        os.chdir(self.workdir) #questionable

        if not data_dicts:
            data_dicts = [{"filename":self.textdir + fn} for fn in self.list_files()]
            self.filequeue =   [{"orig":os.path.abspath(x),
                                 "name":os.path.basename(x),
                                 "size":os.path.getsize(x),
                                 "id":n + 1,
                                 "options":{},
                                 "newpath":self.textdir + os.path.basename(x),
                                 "raw":self.workdir + os.path.basename(x) + ".raw",
                                 "words":self.workdir + os.path.basename(x) + ".words.sorted",
                                 "toms":self.workdir + os.path.basename(x) + ".toms",
                                 "sortedtoms":self.workdir + os.path.basename(x) + ".toms.sorted",
                                 "pages":self.workdir + os.path.basename(x) + ".pages",
                                 "results":self.workdir + os.path.basename(x) + ".results"} for n,x in enumerate(self.list_files())]

        else:
             self.filequeue =   [{"orig":os.path.abspath(d["filename"]),
                                 "name":os.path.basename(d["filename"]),
                                 "size":os.path.getsize(self.textdir + (d["filename"])),
                                 "id":n + 1,
                                 "options":d["options"] if "options" in d else {},
                                 "newpath":self.textdir + os.path.basename(d["filename"]),
                                 "raw":self.workdir + os.path.basename(d["filename"]) + ".raw",
                                 "words":self.workdir + os.path.basename(d["filename"]) + ".words.sorted",
                                 "toms":self.workdir + os.path.basename(d["filename"]) + ".toms",
                                 "sortedtoms":self.workdir + os.path.basename(d["filename"]) + ".toms.sorted",
                                 "pages":self.workdir + os.path.basename(d["filename"]) + ".pages",
                                 "results":self.workdir + os.path.basename(d["filename"]) + ".results"} for n,d in enumerate(data_dicts)]

        self.loaded_files = self.filequeue[:]

        indexed_types = []

        for o_type, path, param in self.parser_defaults["metadata_xpaths"]:
            if o_type not in indexed_types and o_type != "page":
                indexed_types.append(o_type)

        if "doc" not in indexed_types:
            indexed_types = ["doc"] + indexed_types

        for t in indexed_types:
            self.metadata_hierarchy.append([])
            for e_type,path,param in self.parser_defaults["metadata_xpaths"]:
                if t == e_type:
                    if param not in self.metadata_fields:
                        self.metadata_fields.append(param)
                        self.metadata_hierarchy[-1].append(param)
                    if param not in self.metadata_types:
                        self.metadata_types[param] = t
                    else: # we have a serious error here!  Should raise going forward.
                        pass
            if t == "doc":
                for d in data_dicts:
                    for k in d.keys():
                        if k not in self.metadata_fields:
                            self.metadata_fields.append(k)
                            self.metadata_hierarchy[-1].append(k)
                        if k not in self.metadata_types:
                            self.metadata_types[k] = t
                            # don't need to check for conflicts, since doc is first.

        print "%s: parsing %d files." % (time.ctime(),len(self.filequeue))
        procs = {}
        workers = 0
        done = 0
        total = len(self.filequeue)

        while done < total:
            while self.filequeue and workers < max_workers:
                # we want to have up to max_workers processes going at once.

                text = self.filequeue.pop(0) # parent and child will both know the relevant filenames
                metadata = data_dicts.pop(0)
                options = text["options"]
                if "options" in metadata: #cleanup, should do above.
                    del metadata["options"]

                pid = os.fork() # fork returns 0 to the child, the id of the child to the parent.
                # so pid is true in parent, false in child.

                if pid: #the parent process tracks the child
                    procs[pid] = text["results"] # we need to know where to grab the results from.
                    workers += 1
                    # loops to create up to max_workers children at any one time.

                if not pid: # the child process parses then exits.

                    i = open(text["newpath"],"r",)
                    o = open(text["raw"], "w",) # only print out raw utf-8, so we don't need a codec layer now.
                    print "%s: parsing %d : %s" % (time.ctime(),text["id"],text["name"])

                    if "parser_factory" not in options:
                        options["parser_factory"] = self.parser_defaults["parser_factory"]
                    parser_factory = options["parser_factory"]
                    del options["parser_factory"]

                    if "token_regex" not in options:
                        options["token_regex"] = self.parser_defaults["token_regex"]
                    if "xpaths" not in options:
                        options["xpaths"] = self.parser_defaults["xpaths"]
                    if "metadata_xpaths" not in options:
                        options["metadata_xpaths"] = self.parser_defaults["metadata_xpaths"]
                    if "suppress_tags" not in options:
                        options["suppress_tags"] = self.parser_defaults["suppress_tags"]
                    if "pseudo_empty_tags" not in options:
                        options["pseudo_empty_tags"] = self.parser_defaults["pseudo_empty_tags"]

                    if "load_filters" not in options:
                        options["load_filters"] = self.parser_defaults["load_filters"]
                    filters = options["load_filters"]
                    del options["load_filters"]

                    parser = parser_factory(o,text["id"],text["size"],known_metadata=metadata,**options)
                    try:
                        r = parser.parse(i)
                    except RuntimeError:
                        print >> sys.stderr, "parse failure: XML stack explosion : %s" % [el.tag for el in parser.stack]
                        exit(1)
                    i.close()
                    o.close()

                    for f in filters:
                        f(self, text)

                    os.system('gzip -c -5 %s > %s' % (text['raw'], text['raw'] + '.gz'))
                    os.system('rm %s' % text['raw'])
                    os.system('gzip -c -5 %s > %s' % (text['words'], text['words'] + '.gz'))
                    os.system('rm %s' % text['words'])

                    exit()

            #if we are at max_workers children, or we're out of texts, the parent waits for any child to exit.
            pid,status = os.waitpid(0,0) # this hangs until any one child finishes.  should check status for problems.
            if status:
                print "parsing failed for %s" % procs[pid]
                exit()
            done += 1
            workers -= 1
            vec = cPickle.load(open(procs[pid])) #load in the results from the child's parsework() function.
            #print vec
            self.omax = [max(x,y) for x,y in zip(vec,self.omax)]
        print "%s: done parsing" % time.ctime()

    def merge_objects(self, file_num=500):
        print "\n### Merge parser output ###"
        print "%s: sorting words" % time.ctime()
        
        # Make all sorting happen in workdir rather than /tmp
        os.system('export TMPDIR=%s/' % self.workdir)

        words_status = self.merge_words(file_num=file_num)
        print "%s: word sort returned %d" % (time.ctime(),words_status)

        if "words" in self.tables:
            print "\n### Loading word table ###"
            print "concatenating document-order words file"
            for d in self.loaded_files:
                os.system('gunzip -c %s | egrep "^word" >> all_words_ordered' % (d["raw"] + ".gz"))

        tomsargs = "sort -m " + sort_by_id + " " + "*.toms.sorted"
        print "%s: sorting objects" % time.ctime()
        toms_status = os.system(tomsargs + " > " + self.workdir + "all_toms_sorted")
        print "%s: object sort returned %d" % (time.ctime(),toms_status)
        if not self.debug:
            os.system('rm *.toms.sorted')

        pagesargs = "cat *.pages"
        print "%s: joining pages" % time.ctime()
        pages_status = os.system(pagesargs + " > " + self.workdir + "all_pages")
        print "%s: word join returned %d" % (time.ctime(), pages_status)
        if not self.debug:
            os.system("rm *.pages")

    def merge_words(self, file_num):
        """This function runs a multi-stage merge sort on words
        Since PhilLogic can potentially merge thousands of files, we need to split
        the sorting stage into multiple steps to avoid running out of file descriptors"""
        lists_of_words_files = []
        words_files = []
        if file_num > 500:
            file_num = 500  # We want to be conservative and avoid running out of file descriptors

        # First we split the sort workload into chunks of 500 (default defined in the file_num keyword)
        for f in glob(self.workdir + '/*words.sorted.gz'):
            f = os.path.basename(f)
            words_files.append(('<(gunzip -c %s)' % f, self.workdir + '/' + f))
            if len(words_files) ==  file_num:
                lists_of_words_files.append(words_files)
                words_files = []
        if len(words_files):
            lists_of_words_files.append(words_files)

        # Then we run the merge sort on each chunk of 500 files and compress the result
        print "%s: Merging words in batches of %d..." % (time.ctime(), file_num)
        already_merged = 0
        os.system("touch %s" % self.workdir + "/words.sorted.init")
        last_sort_file = self.workdir + "/words.sorted.init"
        for pos, wordlist in enumerate(lists_of_words_files):
            command_list = ' '.join([i[0] for i in wordlist])
            file_list = ' '.join([i[1] for i in wordlist])
            output = self.workdir + "words.sorted.%d.split" % pos
            wordsargs = "sort -m " + sort_by_word + " " + sort_by_id + " " + command_list
            command = '/bin/bash -c "%s | sort -m %s %s - <(gunzip -c %s 2> /dev/null) | gzip -c -5 > %s"' % (wordsargs, sort_by_word, sort_by_id, last_sort_file, output)
            words_status = os.system(command)
            already_merged += file_num
            os.system("rm %s" % last_sort_file)
            last_sort_file = output
            
            print "%s: %d files merged..." % (time.ctime(), already_merged)
            if not self.debug:
                os.system("rm %s" % file_list)
        os.system('mv %s %s' % (last_sort_file, self.workdir + '/all_words_sorted.gz'))

        if words_status != 0:
            print "Word sorting failed\nInterrupting database load..."
            sys.exit()
        return words_status

    def analyze(self):
        print "\n### Create inverted index ###"
        print self.omax
        vl = [max(int(math.ceil(math.log(float(x) + 1.0,2.0))),1) if x > 0 else 1 for x in self.omax]
        print vl
        width = sum(x for x in vl)
        print str(width) + " bits wide."

        hits_per_block = (blocksize * 8) // width
        freq1 = index_cutoff
        freq2 = 0
        offset = 0

        # unix one-liner for a frequency table
        os.system('/bin/bash -c "cut -f 2 <(gunzip -c %s) | uniq -c | sort -rn -k 1,1> %s"' % ( self.workdir + "/all_words_sorted.gz", self.workdir + "/all_frequencies") )

        # now scan over the frequency table to figure out how wide (in bits) the frequency fields are, and how large the block file will be.
        for line in open(self.workdir + "/all_frequencies"):
            f, word = line.rsplit(" ",1) # uniq -c pads output on the left side, so we split on the right.
            f = int(f)
            if f > freq2:
                freq2 = f
            if f < index_cutoff:
                pass # low-frequency words don't go into the block-mode index.
            else:
                blocks = 1 + f // (hits_per_block + 1) #high frequency words have at least one block.
                offset += blocks * blocksize

        # take the log base 2 for the length of the binary representation.
        freq1_l = math.ceil(math.log(float(freq1),2.0))
        freq2_l = math.ceil(math.log(float(freq2),2.0))
        offset_l = math.ceil(math.log(float(offset),2.0))

        print "freq1: %d; %d bits" % (freq1,freq1_l)
        print "freq2: %d; %d bits" % (freq2,freq2_l)
        print "offst: %d; %d bits" % (offset,offset_l)

        # now write it out in our legacy c-header-like format.  TODO: reasonable format, or ctypes bindings for packer.
        dbs = open(self.workdir + "dbspecs4.h","w")
        print >> dbs, "#define FIELDS 9"
        print >> dbs, "#define TYPE_LENGTH 1"
        print >> dbs, "#define BLK_SIZE " + str(blocksize)
        print >> dbs, "#define FREQ1_LENGTH " + str(freq1_l)
        print >> dbs, "#define FREQ2_LENGTH " + str(freq2_l)
        print >> dbs, "#define OFFST_LENGTH " + str(offset_l)
        print >> dbs, "#define NEGATIVES {0,0,0,0,0,0,0,0,0}"
        print >> dbs, "#define DEPENDENCIES {-1,0,1,2,3,4,5,0,0}"
        print >> dbs, "#define BITLENGTHS {%s}" % ",".join(str(i) for i in vl)
        dbs.close()
        print "%s: analysis done" % time.ctime()
        os.system('/bin/bash -c "gunzip -c ' + self.workdir + '/all_words_sorted.gz | pack4 ' + self.workdir + 'dbspecs4.h"')
        print "%s: all indices built. moving into place." % time.ctime()
        os.system("mv index " + self.destination + "/index")
        os.system("mv index.1 " + self.destination + "/index.1")
        #if self.clean:
        #    os.system('rm all_words_sorted')

    def setup_sql_load(self):
        for table in self.tables:
            if table == 'words':
                file_in = self.destination + '/WORK/all_words_ordered'
                indices = [("philo_name",), ('philo_id',), ('parent',), ('byte_start',), ('byte_end',)]
                depth = 7
                compressed = False
            elif table == 'pages':
                file_in = self.destination + '/WORK/all_pages'
                indices = [("philo_id",)]
                depth = 9
                compressed = False
            elif table == 'toms':
                file_in = self.destination + '/WORK/all_toms_sorted'
                indices = [('philo_type',), ('philo_id',)] + self.metadata_fields
                depth = 7
                compressed = False
            post_filter = make_sql_table(table, file_in, gz=compressed, indices=indices, depth=depth)
            self.post_filters.insert(0, post_filter)

    def post_processing(self, *extra_filters):
        print '\n### Post-processing filters ###'
        for f in self.post_filters:
            f(self)
            print 'done.'

        if extra_filters:
            print 'Running the following additional filters:'
            for f in extra_filters:
                print f.__name__ + '...',
                f(self)
                print 'done.'

    def finish(self, **extra_locals):
        """Write important runtime information to the database directory"""
        print "\n### Finishing up ###"
        os.mkdir(self.destination + "/src/")
        os.mkdir(self.destination + "/hitlists/")
        os.chmod(self.destination + "/hitlists/", 0777)
        os.system("mv dbspecs4.h ../src/dbspecs4.h")

        ## Make data directory inaccessible from the outside
        fh = open(self.destination + "/.htaccess", 'w')
        fh.write('deny from all')
        fh.close()

        self.write_db_config(**extra_locals)
        self.write_web_config(**extra_locals)

    def write_db_config(self, **extra_locals):
        """ Write local variables used by libphilo"""
        filename = self.destination + "/db.locals.py"
        db_values = {'metadata_fields': self.metadata_fields,
                     'metadata_hierarchy': self.metadata_hierarchy,
                     'metadata_types': self.metadata_types,
                     'normalized_fields': self.normalized_fields,
                     'debug': self.debug}
        for k, v in extra_locals.items():
            if k != "db_url":  # This should be changed in the load_script
                db_values[k] = v
        db_config = MakeDBConfig(filename, **db_values)
        print >> open(filename, 'w'), db_config
        print "wrote database info to %s." % (filename)

    def write_web_config(self, **extra_locals):
        """ Write configuration variables for the Web application"""
        config_values = {'dbname': os.path.basename(re.sub("/data/?$", "", self.destination)),
                         'db_url': extra_locals['db_url'],
                         'metadata': self.metadata_fields,
                         'facets': [{i: [i]} for i in self.metadata_fields]}
        ## Fetch search examples:
        search_examples = {}
        conn = sqlite3.connect(self.destination + '/toms.db')
        conn.text_factory = str
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        for field in self.metadata_fields:
            object_type = self.metadata_types[field]
            try:
                if object_type != 'div':
                    c.execute('select %s from toms where philo_type="%s" and %s!="" limit 1' % (field, object_type, field))
                else:
                    c.execute('select %s from toms where philo_type="div1" or philo_type="div2" or philo_type="div3" and %s!="" limit 1' % (field, field))
            except sqlite3.OperationalError:
                continue
            try:
                search_examples[field] = c.fetchone()[0].decode('utf-8', 'ignore')
            except (TypeError, AttributeError):
                continue
        config_values['search_examples'] = search_examples
    
        filename = self.destination + "/web_config.cfg"
        web_config = MakeWebConfig(filename, **config_values)
        print >> open(filename, 'w'), web_config
        print "wrote Web application info to %s." % (filename)

def shellquote(s):
    return "'" + s.replace("'", "'\\''") + "'"

def handle_command_line(argv):
    usage = "usage: %prog [options] database_name files"
    parser = OptionParser(usage=usage)
    parser.add_option("-w", "--workers", type="int", default="2", dest="workers", help="define the number of cores for parsing")
    parser.add_option("-d", "--debug", action="store_true", default=False, dest="debug", help="add debugging to your load")

    ## Parse command-line arguments
    (options, args) = parser.parse_args(argv[1:])
    try:
        dbname = args[0]
        args.pop(0)
        files = args[:]
        if args[-1].endswith('/') or os.path.isdir(args[-1]):
            files = glob(args[-1] + '/*')
        else:
            files = args[:]
    except IndexError:
        print >> sys.stderr, "\nError: you did not supply a database name or a path for your file(s) to be loaded\n"
        parser.print_help()
        sys.exit()

    workers = options.workers or 2
    debug = options.debug or False

    return dbname,files, workers, True, True, debug


def setup_db_dir(db_destination, template_dir, safe=False, force_delete=False):
    try:
        os.mkdir(db_destination)
    except OSError:
        if force_delete: # useful to run db loads with nohup
            os.system('rm -rf %s' % db_destination)
            os.mkdir(db_destination)
        else:
            if not safe:
                print "The database folder could not be created at %s" % db_destination
                print "Do you want to delete this database? Yes/No"
                choice = raw_input().lower()
                if choice.startswith('y'):
                    os.system('rm -rf %s' % db_destination)
                    os.mkdir(db_destination)
                else:
                    sys.exit()
            else:
                sys.exit()

    if template_dir:
        for f in os.listdir(template_dir):
            if f != "data":
                cp_command = "cp -r %s %s" % (template_dir+f,db_destination+"/"+f)
                os.system(cp_command)

        os.system("chmod -R 777 %s/app/assets/css" % db_destination)
        os.system("chmod -R 777 %s/app/assets/js" % db_destination)

