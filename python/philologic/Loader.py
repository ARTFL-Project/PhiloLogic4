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

from philologic.utils import OutputHandler

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

        if debug == True:
            self.clean = False
            self.verbose = True
        else:
            self.clean = True
            self.verbose = False

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
        indexed_types = []

        for o_type, path, param in self.parser_defaults["metadata_xpaths"]:
            if o_type not in indexed_types and o_type != "page":
                indexed_types.append(o_type)

        for t in indexed_types:
            self.metadata_hierarchy.append([])
            for e_type,path,param in self.parser_defaults["metadata_xpaths"]:
                if t == e_type:
                    if param not in self.metadata_fields:
                        self.metadata_fields.append(param)
                        self.metadata_hierarchy[-1].append(param)
                    if param not in self.metadata_types:
                        self.metadata_types[param] = t

        #sys.stdout = OutputHandler(console=console_output, log=log)

    def setup_dir(self,path):
        os.mkdir(path)
        self.workdir = path + "/WORK/"
        self.textdir = path + "/TEXT/"
        os.mkdir(self.workdir)
        os.mkdir(self.textdir)
        self.destination = path
        
    def add_files(self,files):
        for f in files:
            os.system("cp %s %s" % (f,self.textdir))
            
    def status(self):
        pass
    
    def list_files(self):
        return os.listdir(self.textdir)
        
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
                    
                    if self.clean:
                        command = 'rm %s' % text['raw']
                        os.system(command)                    
                    
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
    
    def merge_objects(self):
        print "\n### Merge parser output ###"
        wordsargs = "sort -m " + sort_by_word + " " + sort_by_id + " " + "*.words.sorted"
#        words_result = open(self.workdir + "all_words_sorted","w")
        print "%s: sorting words" % time.ctime()
#        words_status = subprocess.call(wordargs,0,"sort",stdout=words_result,shell=True)
        words_status = os.system(wordsargs + " > " + self.workdir + "all_words_sorted")
        print "%s: word sort returned %d" % (time.ctime(),words_status)
        if self.clean:
            os.system('rm *.words.sorted')

        tomsargs = "sort -m " + sort_by_id + " " + "*.toms.sorted"
#        toms_result = open(self.workdir + "all_toms_sorted","w")
        print "%s: sorting objects" % time.ctime()
#        toms_status = subprocess.call(tomsargs,0,"sort",stdout=toms_result,shell=True)                                 
        toms_status = os.system(tomsargs + " > " + self.workdir + "all_toms_sorted")
        print "%s: object sort returned %d" % (time.ctime(),toms_status)
        if self.clean:
            os.system('rm *.toms.sorted')
        
        pagesargs = "cat *.pages"
#        pages_result = open(self.workdir + "all_pages","w")
        print "%s: joining pages" % time.ctime()
#        pages_status = subprocess.call(pagesargs,0,"cat",stdout=pages_result,shell=True)
        pages_status = os.system(pagesargs + " > " + self.workdir + "all_pages")
        print "%s: word join returned %d" % (time.ctime(), pages_status)
         
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
        os.system("cut -f 2 %s | uniq -c | sort -rn -k 1,1> %s" % ( self.workdir + "/all_words_sorted", self.workdir + "/all_frequencies") )
        
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
        os.system("pack4 " + self.workdir + "dbspecs4.h < " + self.workdir + "/all_words_sorted")
        print "%s: all indices built. moving into place." % time.ctime()
        os.system("mv index " + self.destination + "/index")
        os.system("mv index.1 " + self.destination + "/index.1") 
        #if self.clean:
        #    os.system('rm all_words_sorted')

    def setup_sql_load(self):
        for table in self.tables:
            if table == 'words':
                file_in = self.destination + '/WORK/all_words_sorted'
                indices = [("philo_name", "%s_ancestor" % self.default_object_level), ('philo_id',)]
                depth = 7
            elif table == 'pages':
                file_in = self.destination + '/WORK/all_pages'                
                indices = [("philo_id",)]
                depth = 9
            elif table == 'toms':
                file_in = self.destination + '/WORK/all_toms_sorted'
                indices = [('philo_type',), ('philo_id',)] + self.metadata_fields
                depth = 7
            post_filter = make_sql_table(table, file_in, indices=indices, depth=depth)
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
        print "\n### Finishing up ###"
        os.mkdir(self.destination + "/src/")
        os.mkdir(self.destination + "/hitlists/")
        os.chmod(self.destination + "/hitlists/", 0777)
        os.system("mv dbspecs4.h ../src/dbspecs4.h")
        
        db_locals = open(self.destination + "/db.locals.py","w") 

        print >> db_locals, "metadata_fields = %s" % self.metadata_fields
        print >> db_locals, "metadata_hierarchy = %s" % self.metadata_hierarchy
        print >> db_locals, "metadata_types = %s" % self.metadata_types
        print >> db_locals, "db_path = '%s'" % self.destination
        print >> db_locals, "normalized_fields = %s" % self.normalized_fields
        print >> db_locals, "debug = %s" % self.debug
        for k,v in extra_locals.items():
            print >> db_locals, "%s = %s" % (k,repr(v))

        print "wrote metadata info to %s." % (self.destination + "/db.locals.py")        

def handle_command_line(argv):
    usage = "usage: %prog [options] database_name files"
    parser = OptionParser(usage=usage)
    parser.add_option("-q", "--quiet", action="store_true", dest="quiet", help="suppress all output")
    parser.add_option("-l", "--log", default=False, dest="log", help="enable logging and specify file path")
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
        
    ## Number of workers used for parsing: you can define your own value on the
    ## command-line, stay with the default, or define your own value here
    workers = options.workers or 2
    
        
    ## Define the type of output you want. By default, you get console output for your database
    ## load. You can however set a quiet option on the command-line, or set console_output
    ## to False here.
    console_output = True
    if options.quiet:
        console_output = False
        
    ## Define a path for a log of your database load. This option can be defined on the command-line
    ## or here. It's disabled by default.
    log = options.log or False
    
    ## Set debugging if you want to keep all the parsing data, as well as debug the templates
    debug = options.debug or False
    
    return dbname,files, workers, console_output, log, debug


def setup_db_dir(db_destination, template_dir):
    try:
        os.mkdir(db_destination)
    except OSError:
        ## maybe test to see what db_destination is
        print "The database folder could not be created at %s" % db_destination
        print "Do you want to delete this database? Yes/No"
        choice = raw_input().lower()
        if choice.startswith('y'):
            os.system('rm -rf %s' % db_destination)
            os.mkdir(db_destination)
        else:
            sys.exit()
    
    if template_dir:
        os.system("cp -r %s* %s" % (template_dir,db_destination))
        os.system("cp %s.htaccess %s" % (template_dir,db_destination))

                
# a quick utility function
#def load(path,files,filters=default_filters,xpaths=None,metadata_xpaths=None,workers=4):
#    l = Loader(path)    
#    l.add_files(files)
#    l.parse_files(workers,filters,xpaths,metadata_xpaths)
#    l.merge_objects()
#    l.analyze()
#    l.make_tables()
#    l.finish()
        
if __name__ == "__main__":
    os.environ["LC_ALL"] = "C" # Exceedingly important to get uniform sort order.
    os.environ["PYTHONIOENCODING"] = "utf-8"
    
    usage = "usage: philoload.py destination_path texts ..."
    
    try :
        destination = sys.argv[1]
    except IndexError:
        print usage
        exit()
        
    texts = sys.argv[2:]
    if len(sys.argv[2:]) == 0:
        print usage
        exit()

    load(destination,texts)
    
    print "done"
