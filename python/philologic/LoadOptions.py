#!/usr/bin env python

import imp
import os
import sys
from glob import glob
from optparse import OptionParser

from philologic import Loader, LoadFilters, Parser, PostFilters

# Load global config
config_file = imp.load_source("philologic4", "/etc/philologic/philologic4.cfg")

if config_file.url_root == None:
    print >> sys.stderr, "url_root variable is not set in /etc/philologic/philologic4.cfg"
    print >> sys.stderr, "See INSTALLING in your PhiloLogic distribution."
    exit()
elif config_file.web_app_dir == None:
    print >> sys.stderr, "web_app_dir variable is not set in /etc/philologic/philologic4.cfg"
    print >> sys.stderr, "See INSTALLING in your PhiloLogic distribution."
    exit()
elif config_file.database_root == None:
    print >> sys.stderr, "database_root variable is not set in /etc/philologic/philologic4.cfg"
    print >> sys.stderr, "See INSTALLING in your PhiloLogic distribution."
    exit()


class LoadOptions(object):
    def __init__(self):
        self.values = {}
        self.values["database_root"] = config_file.database_root
        self.values["url_root"] = config_file.url_root
        self.values["web_app_dir"] = config_file.web_app_dir
        self.values["destination"] = "./"
        self.values["default_object_level"] = Loader.DEFAULT_OBJECT_LEVEL
        self.values["navigable_objects"] = Loader.NAVIGABLE_OBJECTS
        self.values["load_filters"] = LoadFilters.DefaultLoadFilters
        self.values["post_filters"] = PostFilters.DefaultPostFilters
        self.values["plain_text_obj"] = []
        self.values["parser_factory"] = Parser.Parser
        self.values["word_regex"] = Parser.DefaultWordRegex
        self.values["punct_regex"] = Parser.DafaultPunctRegex
        self.values["token_regex"] = Parser.DefaultTokenRegex
        self.values["xpaths"] = Parser.DefaultXPaths
        self.values["metadata_xpaths"] = Parser.DefaultMetadataXPaths
        self.values["pseudo_empty_tags"] = []
        self.values["suppress_tags"] = []
        self.values["cores"] = 2
        self.values["dbname"] = ""
        self.values["db_url"] = ""
        self.values["files"] = []
        self.values["sort_order"] = ["date", "author", "title", "filename"]
        self.values["header"] = "tei"
        self.values["debug"] = False

        if self.database_root is None or self.url_root is None:
            print >> sys.stderr, "Please configure the loader script before use."
            print >> sys.stderr, "See INSTALLING in your PhiloLogic distribution."
            sys.exit()

        self

    def setup_parser(self):
        usage = "usage: %prog [options] database_name files"
        parser = OptionParser(usage=usage)
        parser.add_option("-a",
                          "--web_app_dir",
                          type="string",
                          dest="web_app_dir",
                          help="Define the location of the web app directory")
        parser.add_option("-c", "--cores", type="int", dest="cores", help="define the number of cores for parsing")
        parser.add_option("-d", "--debug", type="string", dest="debug", help="Set debug to true or false")
        parser.add_option("-e", "--pseudo_empty_tags", type="string", dest="pseudo_empty_tags", help="?")
        parser.add_option("-f",
                          "--parser_factory",
                          type="string",
                          dest="parser_factory",
                          help="Define parser to use for file parsing")
        # parser.add_option("-h", "--header", type="string", dest="header", help="Set header type for parsing")
        parser.add_option("-L",
                          "--load_filters",
                          type="string",
                          dest="load_filters",
                          help="Define filters as a list of functions to call")
        parser.add_option("-m",
                          "--metadata_xpaths",
                          type="string",
                          dest="metadata_xpaths",
                          help="Define metadata xpaths for the XML parser")
        parser.add_option("-n",
                          "--navigable_objects",
                          type="string",
                          dest="navigable_objects",
                          help="Define navigable objects separated by comma")
        parser.add_option("-o",
                          "--default_object_level",
                          type="string",
                          dest="default_object_level",
                          help="Define default object level for navigation")
        parser.add_option("-P",
                          "--post_filters",
                          type="string",
                          dest="post_filters",
                          help="Define filters to run after parsing")
        parser.add_option("-p",
                          "--punct_regex",
                          type="string",
                          dest="punct_regex",
                          help="Define punctuation regex to split sentences")
        parser.add_option("-r",
                          "--token_regex",
                          type="string",
                          dest="token_regex",
                          help="Define regex to use for tokenizing")
        parser.add_option("-s",
                          "--suppress_tags",
                          type="string",
                          dest="suppress_tags",
                          help="Define tags where content will not be indexed")
        parser.add_option("-t",
                          "--plain_text_obj",
                          type="string",
                          dest="plain_text_obj",
                          help="List objects to generate plain text files")
        parser.add_option("-w",
                          "--word_regex",
                          type="string",
                          dest="word_regex",
                          help="Define regex to tokenize words")

        parser.add_option("-x", "--xpaths", type="string", dest="xpaths", help="Define xpaths for the XML parser")

        return parser

    def parse(self, argv):
        ''' Parse command-line arguments'''
        parser = self.setup_parser()
        options, args = parser.parse_args(argv[1:])
        try:
            self.values['dbname'] = args[0]
            args.pop(0)
            if args[-1].endswith('/') or os.path.isdir(args[-1]):
                self.values['files'] = glob(args[-1] + '/*')
            else:
                self.values["files"] = args[:]
        except IndexError:
            print >> sys.stderr, ("\nError: you did not supply a database name "
                                  "or a path for your file(s) to be loaded\n")

            parser.print_help()
            sys.exit()
        for a in dir(options):
            if not a.startswith('__') and not callable(getattr(options, a)):
                value = getattr(options, a)
                if value != None:
                    self.values[a] = value
        self.update()

    def update(self):
        self.values["token_regex"] = "%s|%s" % (self.word_regex, self.punct_regex)
        self.values["db_url"] = os.path.join(self.url_root, self.dbname)
        self.values["db_destination"] = os.path.join(self.database_root, self.dbname)
        self.values["data_destination"] = os.path.join(self.db_destination, "data")
        self.values["load_filters"] = LoadFilters.set_load_filters(navigable_objects=self.navigable_objects)
        if self.plain_text_obj:
            plain_text_filter = LoadFilters.store_in_plain_text(*self.plain_text_obj)
            self.load_filters.append(plain_text_filter)
        if self.debug:
            print load_options

    def __getitem__(self, item):
        return self.values[item]

    def __getattr__(self, attr):
        return self.values[attr]

    def __setitem__(self, attr, value):
        self.values[attr] = value
        if attr == "dbname":
            self.db_url = os.path.join(self.database_root, self.dbname)

    def __contains__(self, key):
        if key in self.values:
            return True
        else:
            return False

    def __iter__(self):
        for i in self.values:
            yield i

    def __str__(self):
        string_list = []
        for i in self.values:
            string_list.append("%s: %s" % (i, self.values[i]))
        return "\n".join(string_list)
